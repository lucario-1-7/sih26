# File Manifest

Every file in this repository: what it does, what goes in, what comes out.

Nothing here is application code yet — this is the plan plus the artifacts that de-risk
building it. The three ML models are real, trained, and measured.

---

## Run order

Read the arrows as "needs this first".

```
seed/capability_taxonomy.json ─┐
seed/institutions.json ────────┼─► seed/validate_seed.py      (integrity gate)
                               │
                               └─► ai/scoring_reference.py    (scoring maths + parity oracle)

ai/data/domain_train.csv ──► ai/models/train_domain.py ──► artifacts/domain_clf.joblib ─┐
        │                            │                                                  │
        │                            └─ uses ─► ai/models/dataprep.py                    │
        │                                       ai/models/embedder.py                    │
        │                                                                                │
ai/data/field_intensity_train.csv ──► ai/models/train_field.py ──► field_clf.joblib ─────┤
                                              │                                          │
                                              └─ chains the domain model for its prior ──┘
                                                                                         │
                                                          ai/models/predict.py ◄──────────┘
                                                          (loads both, serves /ai/analyze)
```

**Order matters in one place:** `train_domain.py` must run before `train_field.py`. The field
model chains the domain classifier to source its prior, and on the `tfidf` backend it also
reuses the encoder that `train_domain.py` fitted. Run it the other way and the field model
silently falls back to a neutral prior, costing ~0.05 macro-F1.

```bash
python ai/models/train_domain.py      # ~6 s
python ai/models/train_field.py       # ~2 s
python ai/models/predict.py           # end-to-end demo
python ai/scoring_reference.py        # scoring maths, no deps
python seed/validate_seed.py          # seed integrity, no deps
```

---

## `ai/models/` — the three models

### `embedder.py` — Model 1, the shared representation · 230 lines

| | |
|---|---|
| **Does** | Wraps the sentence encoder. One forward pass per text, reused by five consumers: domain classification, field intensity, duplicate search, institution matching, solution replication. |
| **Input** | `list[str]` of normalised text |
| **Output** | `np.ndarray (n, 384)`, float32, **L2-normalised** |
| **Artifacts** | reads/writes `artifacts/embed_cache/*.pkl`; `artifacts/tfidf_encoder.joblib` on the fallback backend |

Two backends, selected by `SOCIOSOLVE_BACKEND`:

- `transformer` (default) — `paraphrase-multilingual-MiniLM-L12-v2`, 384-d, CPU, ~20 ms/doc.
  Needs the weights on disk.
- `tfidf` — TF-IDF over character n-grams → TruncatedSVD → 384-d. Pure scikit-learn, **no
  download**. Exists as the emergency fallback *and* as the ablation baseline.

**Gotchas.** `normalize_embeddings=True` is load-bearing, not a leftover default — cosine
becomes a dot product, pgvector's `<=>` behaves, and cluster centroids stay meaningful. The
disk cache is keyed by `(backend, model_name, text)` so switching encoders can never serve
stale vectors. `fit_tfidf()` must be called on the **training split only**; fitting on
everything leaks test vocabulary into the representation.

Run it standalone to print a cross-lingual sanity check (EN/HI/Hinglish of the same sentence
should be close; an unrelated English sentence clearly further).

---

### `train_domain.py` — Model 2, domain classification · 256 lines

| | |
|---|---|
| **Does** | Trains a multinomial logistic regression over the 384-d embedding to pick 1 of 11 domains. |
| **Input** | `ai/data/domain_train.csv` — 1,320 rows, columns `id,text,domain,language` |
| **Output** | `artifacts/domain_clf.joblib` (19 KB) + `artifacts/domain_metrics.json` |
| **Prints** | held-out macro-F1, per class, **per language**, confidence-gate analysis, confusions, zero-shot ablation |

**Measured** (1056/264 split, `tfidf` backend): macro-F1 **0.850**, accuracy 0.852.
Zero-shot fallback 0.474. Per language: English 0.866 · Hinglish 0.858 · Hindi 0.794.
Confidence gate at 0.55 → **0.967** accuracy above, 0.699 below.

The joblib bundle contains `{model, labels, encoder, backend, confidence_gate, version}`.

**Why LR and not a fine-tuned transformer:** a few points of macro-F1 for hours of GPU time,
a much bigger artifact, and a model you cannot explain. Same trade as the linear scoring
model — accuracy sacrificed for auditability, deliberately.

Also defines `DOMAIN_PROTOTYPES` (the zero-shot fallback labels) and `macro_f1()`, both
imported by other modules.

---

### `train_field.py` — Model 3, field intensity · 337 lines

| | |
|---|---|
| **Does** | Trains a 3-class LR, then blends it with a lexical signal and a domain prior into one continuous number. |
| **Input** | `ai/data/field_intensity_train.csv` — 250 rows, `id,text,label`; plus `artifacts/domain_clf.joblib` for the chained prior |
| **Output** | `artifacts/field_clf.joblib` (7 KB) + `artifacts/field_metrics.json` |

```
field_intensity = 0.90·P_model + 0.05·keyword_ratio + 0.05·domain_prior
label = FIELD_HEAVY (≥.66) · HYBRID (.4–.66) · REMOTE_ANALYTICAL (<.4)
```

Output is **continuous on purpose** — it is consumed as a number by three subsystems
(geo discount in matching, dedup radius `d₀`, whether a local partner is mandatory). A hard
enum would throw away the middle and force a special case into all three.

**The weights are fitted, not guessed.** The plan originally said `0.55/0.25/0.20`, written
before data existed. Measured: model only **0.732**, a-priori blend **0.717** *(worse than no
blend)*, fitted `0.90/0.05/0.05` blend **0.769**. Tuning runs on out-of-fold **training**
predictions only, so the held-out number stays honest.

**Two things worth copying.** `P_model` is posterior-weighted intensity
(`P(FIELD)·1.0 + P(HYBRID)·0.5 + P(REMOTE)·0.0`), not `P(FIELD_HEAVY)` — it uses the whole
distribution instead of discarding second place. And the script **chains the domain
classifier** to source its prior, exactly as production does, instead of evaluating with a
neutral 0.5 and measuring a blend nobody ships.

**Assertion that must hold:** mean intensity by true class must increase monotonically —
measured 0.248 → 0.582 → 0.727. If it doesn't, matching is being driven by noise.

---

### `predict.py` — inference, all three models · 290 lines

| | |
|---|---|
| **Does** | The body of `POST /ai/analyze`. One embedding pass, then three cheap heads over it. |
| **Input** | `analyze(text: str, language: str = "auto")` |
| **Output** | dict: `embedding[384]`, `domain`, `domain_confidence`, `domain_alternatives`, `domain_needs_review`, `field_intensity`, `field_label`, `field_explanation`, `field_signals`, `required_capabilities[]`, `ai_meta{}` |
| **Latency** | ~50–90 ms with the transformer (embedding dominates); <1 ms after |

Also does **capability extraction** — multi-label zero-shot cosine against the 30-code
taxonomy in `seed/capability_taxonomy.json`. No training data needed.

**Degradation is part of the contract.** Every model is optional at runtime; a missing or
unloadable artifact produces a documented fallback, never a 500:

| Missing | Falls back to |
|---|---|
| `domain_clf.joblib` | zero-shot prototype cosine (same embedding, no artifact) |
| `field_clf.joblib` | domain prior + keyword ratio, reweighted |
| capability taxonomy | empty list |

**One hard limitation.** Capability extraction **requires the transformer backend** and
refuses to run without it. It is pure semantic matching between "hand pumps keep breaking
down" and "Civil / hydrology / groundwater" — no shared characters, so char n-grams return
nonsense (`ORG_INCUBATION` for a hand-pump report) and nothing at all for Hindi. Since the
consortium builder consumes these codes, an empty list is a visible failure and a wrong list
is an invisible one. It returns the empty list.

---

### `dataprep.py` — shared data preparation · 267 lines

| | |
|---|---|
| **Does** | Load CSV → normalise → drop exact duplicates → group near-duplicates into blocks → stratified split **on blocks** |
| **Input** | CSV path + label column name |
| **Output** | `(train: list[Row], test: list[Row], report: PrepReport)` |

**Why this is not optional.** Both datasets are LLM-generated, and LLM corpora reliably
contain near-duplicate rows. If a duplicate pair straddles the train/test split, the test set
is partly memorised and your reported macro-F1 is inflated — which you then quote to a judge.
Confirmed present: 4 near-duplicate pairs in the domain data, 5 in field intensity.

The fix is splitting on **blocks** rather than rows, so a near-duplicate pair can never land
on opposite sides.

Also exports `normalise()` (NFC + whitespace; conservative on purpose — the multilingual
encoder wants real text, and NFC matters because decomposed vs precomposed Devanagari embed
differently).

**Reading its warnings.** The `?? REVIEW` block flags high-overlap pairs with different
labels. Each is *either* a mislabel *or* two rows sharing an LLM sentence frame while
describing genuinely different things. Both occur in this corpus — read them before changing
anything:

- **FI091 vs FI092** — a real mislabel. FI091 is a pure statistical review, tagged `HYBRID`;
  FI092 says nearly the same thing and is `REMOTE_ANALYTICAL`. **Fix FI091.**
- **Domain rows 527 vs 891** — a false positive. Two Hindi rows sharing a sentence frame, one
  about a public toilet (`sanitation`), one about a parking ramp (`urban_infrastructure`).
  Both labels correct; leave them.

---

## `ai/` — scoring

### `scoring_reference.py` — the scoring maths · 525 lines

| | |
|---|---|
| **Does** | Priority, tractability, field-intensity blend, institution matching, consortium set cover, explanation templates |
| **Input** | plain dicts / dataclasses — no DB, no framework, **stdlib only** |
| **Output** | dicts with `score`, `components`, `contributions`, `explanation` |
| **Run** | `python ai/scoring_reference.py` — walks the Torpa hand-pump challenge end to end |

**Its role changed** with the Express backend. It is no longer production code — the scoring
maths executes in TypeScript inside Express (only the model-dependent steps stay in Python).
This file is now the **specification and parity oracle**: the TS port must reproduce it to
`1e-6` on the seeded challenges, and that test is what protects the port.

**Invariant it enforces:** `100 · sum(contributions) == score_exact`, exactly. The scoring
model is linear, so each contribution *is* `wᵢ·xᵢ` — not a SHAP approximation. Round the
contributions once and derive the score from them; rounding both independently makes the
waterfall bars fail to sum to the headline number.

**Swapping in real embeddings** changes exactly one function (`similarity()`) and two
calibration constants (`SIM_LO`/`SIM_HI`). Everything else is final.

---

## `ai/data/` — training corpora

| File | Rows | Columns | Balance |
|---|---|---|---|
| `domain_train.csv` | 1,320 | `id,text,domain,language` | 11 domains × 120; english/hindi/hinglish × 440 |
| `field_intensity_train.csv` | 250 | `id,text,label` | FIELD_HEAVY 85 · HYBRID 85 · REMOTE_ANALYTICAL 80 |

Both are LLM-generated. That is stated openly in the plan (§10) rather than hidden — the
scores measure the model on data cleaner than reality, and should be quoted alongside a
hand-labelled real-text check.

---

## `ai/artifacts/` — generated, not source

| File | Size | Produced by | In git? |
|---|---|---|---|
| `domain_clf.joblib` | 19 KB | `train_domain.py` | yes — small |
| `field_clf.joblib` | 7 KB | `train_field.py` | yes — small |
| `domain_metrics.json` | <1 KB | `train_domain.py` | yes |
| `field_metrics.json` | <1 KB | `train_field.py` | yes |
| `tfidf_encoder.joblib` | 63 MB | `Embedder.fit_tfidf()` | **no** — gitignored |
| `embed_cache/*.pkl` | varies | `Embedder.encode()` | **no** — gitignored |

Everything here regenerates from the two training commands. The metrics JSONs each carry a
`data_caveat` field stating what the number does and does not measure — keep it there.

Model weights never belong in a database BLOB or a git LFS store: bake them into the Docker
image so a deploy can be rolled back.

---

## `docs/` — the plan

| File | Lines | What it is |
|---|---|---|
| `00-master-plan.md` | 1,491 | The full plan, 23 sections: problem analysis, product definition, MVP scope, AI/ML architecture, matching logic, data strategy, schema, APIs, dashboards, risks, judging strategy |
| `01-demo-script.md` | 219 | Minute-by-minute run sheet for the 7-minute judging demo, plus the Q&A drill and what to do when something breaks. **Read this before writing code** — the build serves the demo |
| `02-execution-plan.md` | 175 | Hour-by-hour for 6 people across 6 parallel tracks, with the gates that decide when to cut |
| `schema.sql` | 347 | PostgreSQL + pgvector DDL, 15 tables, plus a record of the 15 that were cut and why |
| `schema-ml.sql` | 404 | The ML slice: vector columns and indexes, model-output columns, scoring/matching artifacts, the write path, the four pgvector queries, and the feedback-loop columns |
| `api-contract.md` | 283 | Concrete request/response shapes for the six endpoints that carry the demo |
| `FILES.md` | — | This file |

`schema-ml.sql` also records a **gap in the base schema**: rejected merge suggestions write no
row anywhere, so you can measure dedup recall but never precision. It gives the `audit_log`
INSERT that fixes it without adding a table.

---

## `seed/` — institutional data

### `institutions.json` — 1,725 lines

25 records: 15 universities/labs, 10 industry/CSR/government partners. Each carries
`id, kind, name, district, lat, lng, units[], capabilities[], metrics{}, data_provenance{}`.

**The honesty mechanism.** Institution names, districts, coordinates and department names are
**real and publicly verifiable**. Capability strengths, project counts, student numbers and
all faculty entries are **demo estimates**. Every record's `data_provenance` says which is
which, per field, so the UI can render a badge:

```json
"data_provenance": { "identity": "PUBLIC_VERIFIED", "departments": "PUBLIC_VERIFIED",
                     "capabilities": "ESTIMATED_DEMO", "faculty": "SYNTHETIC_DEMO" }
```

Two entries (JalTech Sensors, AgriSetu Analytics) are openly fictional, present to demonstrate
startup/MSME matching.

When a judge asks "is this data real?" — and they will — the answer is a field in the schema
and a badge on screen, not a scramble.

### `capability_taxonomy.json` — 30 codes

Controlled vocabulary shared by challenges (`required_capabilities`) and institutions
(`capabilities`). This is what makes matching capability-based rather than keyword-based.
Kinds: `LAB` · `EQUIP` · `SKILL` · `FIELD` · `ORG`.

Deliberately **not** a database table — 30 static rows. `predict.py` embeds the descriptions
in memory at startup; Express imports the labels.

### `validate_seed.py` — 45 lines

| | |
|---|---|
| **Does** | Referential integrity check across the seed files |
| **Input** | both seed JSONs |
| **Output** | errors + warnings to stdout, exit 1 on error |

Catches: unknown capability codes, duplicate institution ids, strengths out of range, missing
`data_provenance`, universities with no units, `active_projects > max_concurrent`, coordinates
outside India, and capability codes held by no institution (challenges requiring them would
match nobody).

Run it in CI and before every demo. It has already caught a bad India bounding box, three
capabilities with no provider, and a missing taxonomy code.

---

## Root

| File | What it is |
|---|---|
| `README.md` | Project overview, the thesis, repo map, the five differentiators, honest scope statement |
| `.gitignore` | Excludes `__pycache__`, `.env`, `node_modules`, `*.bundle`, and the two large regenerable ML artifacts |
| `sociosolve-plan.bundle` | **Not tracked.** A git bundle created to hand the work over while push access was unavailable. Restore with `git clone sociosolve-plan.bundle sih26`. Regenerate: `git bundle create sociosolve-plan.bundle <branch>` |
| `ai/__init__.py`, `ai/models/__init__.py` | Empty. They exist only so `from ai.models.x import y` resolves when scripts are run from the repo root — which is how every training script imports its siblings. Deleting them breaks all four. |

---

## Not in this repo yet

The application itself. Per the plan (§12), that is a monorepo:

```
apps/web     Next.js 15 — five role portals
apps/api     Express 5 + Drizzle — system of record, all Postgres, all scoring
apps/ai      FastAPI — 3 endpoints, stateless, wraps ai/models/predict.py
packages/shared   Zod schemas imported by both web and api
```

`ai/models/` drops into `apps/ai` almost unchanged. `ai/scoring_reference.py` gets ported to
TypeScript inside `apps/api`, with the parity test against the Python original.
