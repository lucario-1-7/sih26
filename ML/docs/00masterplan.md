# Sahyog — Societal Challenge Innovation Platform
### SIH 2026 · Implementation plan for a 24-hour build

> **Problem statement.** A digital platform to crowdsource societal challenges and
> facilitate collaborative problem solving through universities and industry partnerships.

---

## 1. Executive Summary

**The thesis in one line:** the bottleneck in solving India's local societal problems is
not that nobody reports them — it is that a reported problem never gets **matched to the
institution capable of solving it**. Sahyog is a matching and lifecycle engine for that gap.

A grievance portal ends at *"complaint closed."* Sahyog ends at *"a validated solution
exists, was piloted, and its impact was measured — and it can now be replicated in the
seven other blocks with the same problem."*

**What we actually build in 24 hours** is a modular monolith (FastAPI + Postgres/pgvector +
Next.js) with one shared sentence-embedding model powering five capabilities, and a
government-tunable linear scoring system whose explanations are exact rather than
approximated. Everything ships on `docker compose up` and runs on a laptop with the
venue Wi-Fi switched off.

**The five things that make it not-a-grievance-portal:**

| # | Feature | Why a complaint portal cannot have it |
|---|---------|--------------------------------------|
| 1 | **Two-level clustering** — incident → cluster → systemic theme | A portal closes 50 tickets; we detect that those 50 tickets are *one* systemic problem and open *one* innovation programme |
| 2 | **Consortium Builder** (weighted greedy set cover over capabilities) | A portal routes to a jurisdiction. We *assemble a complementary team* across institutions to close a capability gap |
| 3 | **Field-intensity-conditional geography** | A portal routes by who owns the pincode. We route by who can actually build it, with distance mattering only in proportion to how physical the work is |
| 4 | **Solution Registry + replication engine** | One solved problem becomes N solved problems. A closed ticket helps nobody else |
| 5 | **Measured impact with baseline/endline, claimed vs verified** | "Status: resolved" is not an outcome. A 42% drop in downtime is |

**Honest scope statement.** We do not have a labelled Jharkhand societal-challenge dataset.
We say so, on a slide. What we build instead is a system that is *correct with 40 seeded
records and better with 40,000* — and we show exactly how it improves (Section 10).

---

## 2. Problem Understanding

### 2.1 The core problem

Three failures stack on top of each other:

1. **Structuring failure.** A citizen says *"paani nahi aata"* (no water comes). That is not
   yet a problem statement anyone can work on. It lacks domain, scope, affected population,
   root-cause hypothesis, and the capability list needed to solve it.
2. **Aggregation failure.** Forty households report the same broken system as forty separate
   items. Each looks small. Together they are a district-scale engineering problem worth a
   funded project. Nothing in the current stack performs that aggregation.
3. **Matching failure — the real one.** India has ~1,100 universities and ~45,000 colleges
   with labs, faculty, and students who must produce projects anyway. Meanwhile district
   administrations have problems they lack technical capacity to solve. **The two sides do
   not have a channel.** Students build the same generic e-commerce clone; the hand pumps
   stay broken 40 km away.

The government's actual goal is not complaint redressal — that machinery exists (CPGRAMS,
CM helplines). It is to convert **latent civic problems into an innovation pipeline** that
uses academic capacity the state is already paying for.

### 2.2 Stakeholders

| Stakeholder | What they put in | What they get out | Why they show up |
|---|---|---|---|
| **Citizen / community org** | Problem reports, evidence, local ground truth, endline verification | Visible progress, a working solution | Something actually changes |
| **Field assistant** (ASHA, anganwadi, panchayat sevak) | Submits for people who cannot use a smartphone | Recognition, coverage credit | Already their job; removes the digital-divide bias |
| **District administration / validator** | Validation, severity calibration, merge decisions, pilot permission | Prioritised queue, technical capacity for free | Their unsolvable list gets shorter |
| **State department** | Priority themes, scheme budget lines, procurement channel | Portfolio view, evidence for scheme design | Answers "what do we fund next" with data |
| **University / HEI** | Faculty time, labs, student cohorts | Real projects, publications, NAAC/NIRF outreach evidence, NEP community-engagement credits | Needs live problems more than the state needs students |
| **Faculty** | Supervision, methodology | Field data, co-authored papers, consultancy | Field data is genuinely hard to get |
| **Students** | The work | Credited capstone, portfolio, stipend | Better than a clone project |
| **Industry / MSME / startup** | Mentors, components, fabrication, pilot sites | De-risked R&D, talent pipeline, CSR compliance evidence | CSR spend needs auditable outcomes |
| **CSR arms** | Funding | Verified impact numbers per rupee | Section 135 reporting |
| **Incubators / research labs** | Specialised equipment, commercialisation | Deal flow validated by real demand | Pre-qualified problems |

**The critical asymmetry:** universities need real problems *more* than the state needs
students. That asymmetry is the platform's fuel. Every design decision that makes it easier
for a university to say yes is worth more than a feature for the government.

### 2.3 Required workflows

Explicit in the statement: crowdsource challenges; enable university participation; enable
industry participation; support collaborative problem solving.

Implicit, and where the real work is: structure the raw report; validate it; **deduplicate
and aggregate**; prioritise under scarcity; **decide which institution should get it and
why**; form a multi-institution team; track a project through prototype → pilot; measure
impact; report to government; feed learning back.

### 2.4 What success actually means

Vanity metrics we will **not** headline: number of submissions, registered users, page views.

| Tier | Indicator | Why it is the real one |
|---|---|---|
| Pipeline | Challenges **validated** (not submitted) | Submission is free; validation means a human agreed it is real |
| Pipeline | **Match acceptance rate** by institutions | The single best early signal — if universities decline, matching is wrong |
| Output | Projects reaching **Prototype** and **Pilot** | The stage most initiatives die at |
| Output | **Time from validation to institution accepted** | Measures the platform's actual function |
| Impact | Clusters resolved with **verified** baseline→endline | The only claim that survives scrutiny |
| Impact | **Replication count** per solution | Leverage: proof one project served many places |
| Ecosystem | Distinct institutions with ≥1 completed project; industry rupees committed; students credited; patents/startups spun out | Ecosystem health |
| Equity | **District coverage gap** — districts with high deprivation but low submissions | Guards against serving only the loudest districts |

---

## 3. Product Vision

### What Sahyog IS

A **civic R&D marketplace with a routing brain.** Three things:
1. A structuring engine turning unstructured citizen reports into well-formed problem
   statements with domain, capability requirements, priority, and evidence.
2. A matching engine deciding *which institutions, in which roles, together* should work
   on it — with an explanation for every choice.
3. A lightweight project spine tracking the work from acceptance to measured impact.

### What Sahyog IS NOT

- **Not a grievance redressal system.** We do not commit to resolving anything within N days.
  If a problem needs a repair order, it belongs in CPGRAMS — we have an explicit "route to
  grievance system" outcome for exactly that.
- **Not a tender or procurement portal.** No bidding, no payments in scope.
- **Not an LMS or a research repository.**
- **Not a social network.** No feeds, no likes, no follower counts.

### Why universities and industry, specifically

Universities bring the three things a district lacks: **method** (a controlled pilot, not a
guess), **labs** (a water sample tested rather than eyeballed), and **cheap capable labour**
(students who must do a project regardless). Industry brings the three things a university
lacks: **manufacturability**, **money**, and **the maintenance network** that determines
whether a deployed device is alive in eighteen months. Neither side alone completes the
chain. That is precisely why the Consortium Builder exists rather than a single ranked list.

### The government's role

Deliberately **narrow: validator, prioritiser, and procurement channel** — not project
manager. Government validates that a problem is real, sets the weights that define state
priority, grants pilot permission, and buys what works. It does not run the engineering.
Every workflow we build respects that boundary; it is what keeps the model realistic.

### The central loop

```
submission → validation → structuring (domain, capabilities, field intensity)
   → deduplication into a cluster → prioritisation → consortium matching
   → institution acceptance → team formation → proposal → milestones
   → prototype → field testing → pilot → measured impact
   → Solution Registry → replication to matching clusters elsewhere
```

The loop **closes**. Output re-enters as input. That is the difference between a pipeline
and a platform.

---

## 4. Why It Is Not a Grievance Portal

The distinction has to be **visible on screen in under sixty seconds**, or judges will
pattern-match us to every other portal they saw that day.

### 4.1 Two-level clustering: incident, cluster, theme

Two reports of a broken hand pump 40 km apart are **not the same incident** — but they are
the same **archetype**. Collapsing them loses locality; keeping them separate loses the
systemic signal. So we model both:

- **Cluster** = same real-world issue instance. Requires text + geographic + temporal
  agreement. Drives *one project*.
- **Theme** = same class of problem across geography. Text only. Drives *a programme*, and
  is what makes a Secretary sit up: *"this is not 200 complaints, this is one systemic
  maintenance-system failure across 6 districts."*

### 4.2 Consortium Builder

Ranking gives a list. **Set cover gives a team.** We compute the capabilities a challenge
requires, the capabilities the best lead institution has, and then greedily add whichever
partner closes the most remaining *critical* capability per unit of coordination cost.
Output: *"BAU leads. BIT Mesra closes IoT and embedded. CCL closes the maintenance network
and funds it. IIT Madras joins as remote technical collaborator. Coverage 30% → 87%."*
No grievance system has any analogue for this.

### 4.3 Geography that is conditional on physics

A software problem does not care where the developer sits; a hand-pump problem cares
enormously. We compute a continuous `field_intensity ∈ [0,1]` and let it *scale* the
distance penalty. A 1,230 km specialist is nearly disqualified as lead on a field problem
and simultaneously ranks **#1** as technical collaborator. Both are correct, and showing
both on one screen is the sharpest single moment in the demo.

### 4.4 Solution Registry and replication

When a project completes, its solution is embedded and stored. The engine then searches all
open clusters for matches: *"this hand-pump telemetry solution applies to 7 other clusters
across 3 districts — replicate?"* One project becomes district-scale impact. A closed ticket
helps exactly one person.

### 4.5 Impact measured, not asserted

Every project declares indicators up front (`pump_downtime_days`, `households_with_safe_water`)
with a **baseline captured before work starts**. Completion requires an endline with
evidence. The dashboard reports **claimed** and **verified** impact as separate numbers.
A grievance portal's terminal state is a status flag; ours is a measured delta.

### 4.6 (bonus) Academic value routing

Each matched challenge auto-generates a **capstone brief**: scope, disciplines needed,
credit mapping (NEP 2020 community engagement / AICTE activity points), suggested duration,
deliverables. This is the incentive engine — it is how a HOD says yes in one meeting instead
of three.

---

## 5. Stakeholders → Roles → Permissions

| Role | Create | Read | Approve | Notes |
|---|---|---|---|---|
| `CITIZEN` | challenges, feedback, endline confirmation | own challenges, public cluster status | — | Phone OTP in production; password for demo |
| `FIELD_ASSISTANT` | challenges on behalf of citizens | own submissions | — | Carries `on_behalf_of` metadata; equity lever |
| `VALIDATOR` | — | district queue | validate, merge, split, set severity | Cannot change weights |
| `GOV_ADMIN` | themes, priority tags | statewide | scoring weights, pilot permission | Every weight change audited |
| `UNIV_COORDINATOR` | teams, proposals | matched challenges + open board | accept/decline match | Institution-scoped |
| `FACULTY` | milestones, deliverables | own projects | verify milestones | |
| `STUDENT` | milestone updates | own projects | — | |
| `INDUSTRY` | interest, commitments | open board + invitations | commit funding/mentoring | |
| `ADMIN` | everything | everything | everything | Demo reset button lives here |

---

## 6. Core Workflow

```
 CITIZEN / FIELD ASSISTANT
        │  text + photo + GPS pin (Hindi or English)
        ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ INTAKE                                                       │
 │  · normalise → embed (384-d, shared by everything below)     │
 │  · domain classify · capability extract · field intensity    │
 │  · near-duplicate search (vector + geo + time)               │
 │  ≈ 90 ms, synchronous — the citizen sees the analysis        │
 └─────────────────────────────────────────────────────────────┘
        ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ VALIDATION  (human, always)                                  │
 │  · confirm real · set severity/affected · confirm or reject  │
 │    the suggested merge · override any AI field               │
 └─────────────────────────────────────────────────────────────┘
        ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ CLUSTER + SCORE                                              │
 │  priority (7 components) × tractability (4) → triage quadrant│
 └─────────────────────────────────────────────────────────────┘
        ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ MATCH                                                        │
 │  lead track (geo applies) ‖ collaborator track (geo ignored) │
 │  industry role assignment → CONSORTIUM set cover             │
 │  every row carries an exact contribution breakdown           │
 └─────────────────────────────────────────────────────────────┘
        ▼
 accept → team → proposal → approve → milestones → prototype
        → field testing → pilot → impact → SOLUTION REGISTRY
                                              │
                              replication ─────┘  (loop closes)
```

---

## 7. MVP Scope

Ruthless. The rule: **if it cannot appear in the seven-minute demo, it is not built.**

### MUST BUILD — demo fails without these (≈65% of effort)

1. Auth with the 6 demo roles (JWT, seeded accounts, one-click role switcher for the demo).
2. Citizen submission: text + photo + map pin + language toggle.
3. **Live AI analysis card** returned synchronously on submit.
4. Duplicate detection + validator merge, with the priority recomputing visibly.
5. Priority scoring with the **contribution waterfall** and **live weight sliders**.
6. Validator console: queue, validate, edit metadata, merge/split.
7. **Matching: lead track + collaborator track + industry roles + Consortium Builder**, each row explained.
8. University portal: matched challenge → accept → form team → submit proposal.
9. Project lifecycle state machine with milestones; at least one transition performed live.
10. Government dashboard: KPI strip, district map, domain distribution, pipeline funnel, **priority × tractability quadrant**.
11. Citizen status tracker showing the full journey of their report.

### SHOULD BUILD — build only if the E2E path is green by hour 15 (≈20%)

12. Solution Registry + replication suggestions *(highest-value optional — attempt first)*.
13. Industry self-service portal (discover → express interest → commit).
14. In-app notifications (email logged to console, not sent).
15. Impact baseline/endline capture with verification.
16. Hindi input working end to end (multilingual encoder makes this cheap).
17. Capstone brief auto-generation (template fill — 45 minutes, disproportionate judge impact).

### MOCK / SIMULATE — realistic seeded data, no infrastructure (≈15%)

- Historical projects, completed pilots, past impact numbers → all seeded so the dashboard is not empty.
- Email/SMS: written to `notifications` and printed to a visible log pane. **Never** claim it sends.
- Grievance-system import: 5 records with `submitted_via='IMPORT_GRIEVANCE'` demonstrating the adapter.
- Faculty accounts and named faculty: seeded, flagged `SYNTHETIC_DEMO`.
- IVR/voice submission: one slide, zero code.

### FUTURE SCALE — architecturally accommodated, zero hackathon time

Mobile app · offline-first PWA sync · ASR for Santali/Ho/Kurukh voice submission ·
active-learning retraining · federated institution data connectors · DigiLocker/e-Sign ·
fund disbursement · state data-lake integration.

### Explicitly rejected, and why

| Rejected | Reason |
|---|---|
| Microservices | Six people, 24 hours. Service boundaries cost more than they return; a monolith with clean modules refactors later |
| Blockchain | Adds no property we need. An append-only `audit_log` gives the same auditability |
| Fine-tuning / training an LLM | No labelled data, no time, no benefit over embeddings + logistic regression |
| Collaborative-filtering recommender | Cold start with zero interaction history. Content-based matching is the correct answer at n=0 |
| Native mobile + web | Duplicate work. Responsive web covers the demo and real field use |
| Real-time chat | Pure CRUD; nothing to do with turning a problem into a solution |
| Custom OCR / image classification of evidence photos | Fragile, off the critical path. Photos are evidence for humans, not model input |
| Kubernetes | `docker compose` on one VM |

---

## 8. AI/ML Architecture

Every component answers three questions: **what data do we have, what exactly is the model
doing, and can we demonstrate it live?**

### 8.0 The shared representation

```
raw text ─► normalise ─► SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                              │  384-d, ~470 MB, CPU, 15–25 ms/doc
                              ▼
                    ONE embedding, reused by FIVE consumers:
      ① domain classifier  ② duplicate search  ③ capability extraction
      ④ institution expertise matching  ⑤ solution replication search
```

**Why multilingual over `all-MiniLM-L6-v2`:** real submissions in Jharkhand will be Hindi
and Hinglish. The multilingual model puts *"हैंडपंप खराब है"* and *"the hand pump is broken"*
near each other in the same space — which means dedup, classification, and matching all work
across languages **for free**, with no translation step. That single choice buys the entire
multilingual story for ~390 MB and zero extra code.

> **Non-negotiable operational rule.** Pre-download the model into the Docker image and set
> `HF_HUB_OFFLINE=1`. A hackathon venue where `model.encode()` tries to reach huggingface.co
> at demo time is a lost competition. Verify with the laptop in airplane mode at hour 22.

**Why one embedding for everything is the right architecture:** it is one model to load, one
latency budget, one cache, one thing to debug at 4am — and consistency between components
(a challenge matched to a department is measured in the same space that decided its domain).

### 8.A Domain classification

| | |
|---|---|
| **Input** | Normalised challenge text (Hindi/English) |
| **Output** | One of 11 domains + calibrated confidence + top-3 alternatives |
| **Model** | Multinomial **logistic regression** over the 384-d embedding |
| **Training data** | ~1,300 synthetic examples (≈120/domain), LLM-generated *offline before the hackathon*, hand-reviewed, committed as `ai/data/domain_train.csv` |
| **Training cost** | ~4 seconds on CPU. Artifact `domain_clf.joblib`, ~40 KB |
| **Inference** | **< 1 ms** after embedding |
| **Local?** | Entirely |
| **24h realistic?** | Yes — the only real cost is generating the corpus, which happens before the clock starts |

Domains: `education · healthcare · agriculture · water · sanitation · environment · energy ·
urban_infrastructure · accessibility · public_administration · rural_livelihoods`.

**Approach comparison — and why we chose this:**

| Approach | Accuracy | Cost | Verdict |
|---|---|---|---|
| Zero-shot cosine to label prototypes | ~0.62 macro-F1 | zero training | **Fallback.** Ships with no artifacts, degrades gracefully |
| **Embedding + logistic regression on synthetic data** | ~0.85 expected | 4 s train | **PRIMARY.** Trained model with a reportable held-out score, offline, sub-ms |
| Fine-tuned transformer | ~0.88 | hours, GPU | Rejected — +3 points for 20× the cost |
| LLM API classification | ~0.90 | network + latency + cost | Rejected on the critical path. Also invites *"so you just call GPT?"* |

**The fallback is real code, not a sentence in a slide:** `AI_MODE=trained|zeroshot` env var.
If the joblib fails to load, the service logs a warning and serves zero-shot. The demo never
shows a 500.

**What we tell judges:** *"Held-out macro-F1 on synthetic data is X. That number measures
the model, not the world — synthetic data is easier than reality. We also hand-labelled 60
real-sounding reports as an honest check; that score is Y."* Reporting both is more
credible than reporting one inflated number, and pre-empts the obvious question.

### 8.B Deduplication

Three signals, because text alone is wrong in both directions — two different villages use
identical words, and the same incident gets described completely differently.

```
dup_score = 0.60 · cos_sim  +  0.25 · geo_score  +  0.15 · time_score

geo_score  = exp(−distance_km / d₀),   d₀ = 5 km  (field-heavy)
                                       d₀ = 25 km (hybrid)
                                       d₀ = ∞ ⇒ geo_score = 1 (remote/analytical)
time_score = exp(−|Δt| days / 30)
```

`d₀` depends on `field_intensity` for a concrete reason: a broken pump is an issue *at a
point*; "scholarship portal rejects valid applications" is the same issue statewide. One
threshold cannot serve both.

**Blocking** (so we never compare against everything): same or adjacent domain **AND**
within 3·d₀ km **AND** within 180 days. On seeded volumes this is a handful of candidates.

**Thresholds and the governance rule that matters:**

| `dup_score` | Action |
|---|---|
| ≥ 0.82 | **Suggest** merge, pre-ticked in the validator UI |
| 0.70 – 0.82 | Flag as "possible duplicate", shown side-by-side, unticked |
| < 0.70 | New cluster |

> **The system never auto-merges.** A merge is a human decision, is written to `audit_log`
> with the officer's id, and is **always reversible**. Merging *raises* the cluster's
> priority — the citizen's report is aggregated, never discarded. This directly answers the
> sharpest judge question: *"what if your AI wrongly merges a real problem away?"*
> It structurally cannot: no report is ever closed by a merge.

**Clustering:** online nearest-centroid assignment on write (O(candidates), milliseconds),
plus an on-demand **agglomerative re-cluster** (average linkage, cosine, distance threshold
0.25) exposed as a "Re-cluster district" button. Batch re-clustering fixes the drift that
incremental assignment accumulates, and having it as a *button* makes it demoable.

**Theme assignment** (level 2): text-only cosine against theme centroids, threshold 0.72,
no geography. This is what produces *"6 districts, one systemic failure."*

### 8.C Prioritisation

Interpretable by construction — a linear combination of seven normalised components.
Reference implementation: [`ai/scoring_reference.py`](../ai/scoring_reference.py), runnable.

```
Priority = 100 × Σ wᵢ · xᵢ

  reach          0.20   log₁₀(1+affected) / log₁₀(1+100 000)          capped 1
  severity       0.20   severity_level / 4                             validator-set, AI-suggested
  vulnerability  0.15   Σ flag weights (children .20, PwD .20, ST/SC .20,
                        elderly .15, women's safety .15, BPL .10)      capped 1
  corroboration  0.15   [log₂(1+n_reports) / log₂(1+64)] · e^(−days_since_last/90)
  persistence    0.10   min(1, months_open / 12)
  spread         0.10   min(1, distinct_panchayats / 10)
  gov_priority   0.10   1.0 if tagged to a state mission, else 0.3
```

**Why each transform, specifically:**
- *log on reach* — the jump from 50 to 500 affected people matters far more than 50k to 500k.
- *log₂ saturation on corroboration* — 64 reports is not 64× one report; without saturation,
  one vocal locality dominates the entire state queue.
- *exponential recency decay* — a cluster nobody has re-reported in six months should not
  hold rank against a live one.
- *`gov_priority` floor of 0.3, not 0* — an untagged problem must never score zero on a
  component; that would let a single policy tag dominate the ranking.

**The weights are a database table, not a constant.** `GOV_ADMIN` moves sliders, the queue
re-ranks live, and the change is audited. This converts the standard objection *"who decided
these weights?"* into a feature: **the government did, and here is the audit trail.**

**Priority alone produces a wish-list.** We also compute **Tractability**:

```
Tractability = 100 × ( 0.40 · institutional_fit    (best match score / 100)
                     + 0.25 · solution_precedent   (max cos to registry solutions)
                     + 0.20 · scope_realism        (1 − (months−3)/21, clipped)
                     + 0.15 · data_availability )
```

Plotted as a 2×2 that a Secretary reads in three seconds:

| | **High tractability** | **Low tractability** |
|---|---|---|
| **High priority** | **LAUNCH NOW** | **RESEARCH TRACK** (fund a study first) |
| **Low priority** | **STUDENT PROJECT** (great capstone) | **PARK & MONITOR** |

This 2×2 is the single most "government-useful" artifact in the product, and it costs one
scatter plot.

### 8.D Problem-type classification (field intensity)

**Output is continuous, not a label** — because it feeds a continuous discount, and a hard
PHYSICAL/REMOTE split throws away the useful middle (telemedicine is both).

```
field_intensity = 0.55 · P_model(field | embedding)   ← logistic regression, 3 classes
                + 0.25 · keyword_ratio                 ← lexical sanity check
                + 0.20 · domain_prior                  ← water .85, education .35, public_admin .20

label = FIELD_HEAVY (≥.66) · HYBRID (.4–.66) · REMOTE_ANALYTICAL (<.4)
```

The rule terms are not padding: with ~250 synthetic training rows, the classifier is thin,
and the keyword/prior terms stop it producing an absurd answer on unusual phrasing. As real
labelled data accumulates, raise the model weight and drop the others — the blend is a
config value, and that migration path is itself part of the pitch.

**This single number drives:** the geography weight in matching, the dedup radius `d₀`,
whether local implementation partners are required in the consortium, and whether the
lead/collaborator split is even shown.

### 8.E University matching

Not keyword routing. Seven components, all in [0,1], combined linearly, then discounted by
geography **in proportion to how physical the problem is**.

```
Base = 0.28 · expertise        cos(challenge, department expertise text), top-2 weighted 0.7/0.3
     + 0.18 · research         cos(challenge, research centre / lab text)
     + 0.16 · facility         criticality-weighted coverage of required capability codes
     + 0.14 · implementation   0.45·local_presence + 0.30·community_network + 0.25·field_mobility
     + 0.10 · track_record     log₂(1+completed) / log₂(1+32)
     + 0.08 · capacity         1 − active_projects / max_concurrent
     + 0.06 · students         relevant discipline headcount / 1500, capped

geo_penalty  = 1 − exp(−distance_km / 120)
geo_discount = 1 − (0.55 · field_intensity · geo_penalty)

LEAD score          = 100 · Base · geo_discount
COLLABORATOR score  = 100 · Base                      ← geography deliberately ignored
```

**Why multiplicative-conditional beats "minus a geographic penalty":**
- `field_intensity = 0` ⇒ `geo_discount = 1` **exactly**. Distance is not down-weighted for
  software problems, it is *arithmetically absent*. A subtractive penalty would still leak.
- `field_intensity = 1`, 400 km away ⇒ discount ≈ 0.47 — halved, not eliminated. A distant
  institution that is dramatically better still competes.
- One `λ = 0.55` knob controls exactly how much geography is ever allowed to matter.

**The two-track output is the product decision, not just a formula.** Prototype testing and
pilot deployment require someone who can be on site next Tuesday and again in March.
Research and design do not. So the engine returns **two ranked lists**, and the consortium
draws from both:

> *Torpa hand-pump challenge, field intensity 0.90 — from `ai/scoring_reference.py`:*
>
> | | **Lead track** (geography applies) | **Collaborator track** (geography ignored) |
> |---|---|---|
> | 1 | BAU Ranchi **40.1** — 50 km ×0.83 | **IIT (ISM) Dhanbad 51.8** — 156 km |
> | 2 | Ranchi University **38.7** — 44 km | BAU Ranchi 48.3 |
> | 3 | BIT Mesra **34.7** — 52 km | Ranchi University 45.6 |
> | 4 | … | **IIT Madras 43.3** — 1,230 km |
> | | *IIT (ISM) is #5 here* · *IIT Madras is #10* | |

Same challenge, same instant, two different questions. **IIT (ISM) Dhanbad has the strongest
groundwater expertise in the pool and is still only #5 as lead** — 156 km on a field-heavy
problem costs it 36%. It is #1 as collaborator. IIT Madras, at 1,230 km, loses half its score
and falls to #10 as lead while holding #4 as collaborator. Nearby institutions run the field
work; distant specialists contribute expertise. **That screen is the demo.**

**Calibration — the detail that decides whether this works.** Sentence-transformer cosines
on domain text bunch between ~0.20 and ~0.70, not [0,1]. Feeding raw cosine into a weighted
sum silently shrinks the semantic weights to a third of nominal, and **student headcount
starts outranking subject expertise**. We hit exactly this while building the reference
implementation. Fix: one fixed affine rescale with documented anchors (p5/p95 of the real
cosine distribution). *Fixed, not pool-relative* — with pool-relative normalisation, adding
one weak candidate changes everyone's score, and a government system must be able to compare
today's score with last month's.

### 8.F Industry matching

Same skeleton, different components — and crucially it outputs a **role**, not a rank.

```
Fit = 0.30 · tech_domain       cos(challenge, technology expertise text)
    + 0.20 · sector_relevance  sector ↔ domain affinity table
    + 0.15 · facility          capability coverage (fabrication, IoT, manufacturing)
    + 0.15 · deployment_reach  1 if the site's district ∈ geographic_reach, else 0.3
    + 0.10 · csr_alignment     challenge domain ∈ declared CSR themes
    + 0.10 · engagement        past completed collaborations
```

Then `role = argmax` over role-specific sub-scores:
`FUNDER` (CSR capacity + theme) · `MENTOR` (mentors available + domain) ·
`FAB_PARTNER` (fabrication/manufacturing) · `DEPLOY_PARTNER` (maintenance/community network) ·
`PILOT_HOST` (local presence + facility) · `DATA_PARTNER` (holds relevant operational data).

*"Tata Steel Foundation → **FUNDER**: water & sanitation is a declared CSR theme, Khunti is
in its operating footprint, ₹2.5 Cr annual CSR capacity."* Far more actionable than "87% match."

### 8.G Explainability

**Every** AI output carries a human-readable explanation. Three properties:

1. **Exact, not approximated.** The scoring model is linear, so each component's contribution
   *is* `wᵢ · xᵢ`. No SHAP, no LIME, no sampling — the explanation **is** the model. This is a
   deliberate trade of a few accuracy points for total auditability, which is the right trade
   for a government decision-support system, and it is a strong answer to "explain your AI."
2. **Evidence-linked.** Not "expertise 0.81" but *"Dept. of Environmental Science &
   Engineering — 'groundwater contamination, fluoride and iron removal' matched at 0.81."*
3. **Counterfactual.** Every recommendation shows *"why not #2"*: the specific components
   where the runner-up lost.

Generated from **templates, not an LLM** — deterministic, offline, instant, and it says the
same thing every time a judge clicks it.

> *"IIT (ISM) Dhanbad ranks **#1 on the collaborator track and #5 as lead**. Its Department of
> Environmental Science & Engineering matches this groundwater challenge at 0.64 (calibrated),
> the highest in the pool, and it holds a water-quality laboratory (strength 0.95). At 156 km
> from Torpa with field intensity 0.90, geography removes **36%** of its lead score — enough to
> place four nearer institutions ahead of it for on-site work, not enough to exclude it from
> the team. It cannot cover: EQ_ELECTRONICS_IOT, SKILL_EMBEDDED, FIELD_MAINTENANCE_NET,
> FIELD_COMMUNITY_NETWORK, ORG_CSR_FUNDING."*

Note the shape of that sentence: it names the *evidence* (a specific department and its
matched text), the *arithmetic* (36%, and where it came from), and the *limits* (five
capabilities it cannot cover). An explanation that only reports a score is not an explanation.

---

## 9. Matching & Routing Logic — worked example

Torpa block, Khunti district (22.99 N, 85.21 E). Required capabilities extracted from the
cluster text, with criticality:

```
SKILL_CIVIL_HYDRO .9 · LAB_WATER_QUALITY .9 · FIELD_MAINTENANCE_NET .9
EQ_ELECTRONICS_IOT .8 · FIELD_COMMUNITY_NETWORK .8 · SKILL_EMBEDDED .7
ORG_CSR_FUNDING .6 · EQ_FABRICATION .5 · SKILL_ML_DATA .5
```

**Consortium Builder** (weighted greedy set cover; coordination cost grows with distance ×
field intensity; only `kind='UNIVERSITY'` is lead-eligible — a state department cannot lead
a student innovation project):

| Step | Added | Role | Marginal capability closed | Coverage |
|---|---|---|---|---|
| 0 | Birsa Agricultural University | **LEAD** | highest lead score (40.1), on-site | 30% |
| 1 | BIT Mesra | ACADEMIC_PARTNER | IoT, embedded, fabrication, ML | 65% |
| 2 | Central Coalfields Ltd (CSR) | **FUNDER** | maintenance network, CSR funding | 82% |
| 3 | IIT Madras | **TECHNICAL_COLLABORATOR** | residual water-treatment depth | 87% |

`unmet_critical: none`. Stop condition: coverage ≥ 85% or 4 partners.

**Why greedy is the right algorithm here.** Set cover is NP-hard; greedy is the standard
`(1 + ln n)`-approximation, runs in microseconds over a few hundred institutions, and — the
property that actually matters — **produces a step-by-step trace that is itself the
explanation.** Each addition names the capability it closed and the coverage delta. An exact
solver would be slower, no better in practice at this size, and unexplainable.

**Termination is deliberately conservative.** Four partners maximum, because a six-partner
consortium is a coordination failure disguised as thoroughness. If critical capabilities
remain unmet, we say so rather than padding the team — `unmet_critical` is surfaced to the
validator as *"no institution in the registry can cover X; consider a state tender."*
Knowing what the ecosystem **cannot** do is genuinely useful government intelligence.

---

## 10. Data Strategy

**We do not have a labelled Jharkhand societal-challenge dataset. We say so, plainly, on a
slide.** Pretending otherwise is the fastest way to lose credibility with a judge who has
seen forty decks. What we show instead is a system correct at n=40 and better at n=40,000,
with an explicit path between them.

### Real data (sourced, verifiable)

| Data | Source | Status |
|---|---|---|
| District/block/GP names + LGD codes | Local Government Directory | Real, downloadable CSV |
| Institution names, cities, coordinates, department names | Institution websites, AISHE, NIRF | **Real and publicly verifiable** |
| Government mission themes (Jal Jeevan, Swachh Bharat, NEP, PMKSY) | Scheme documents | Real |
| Problem archetypes | News reports, CAG audits, district plans, published rural-water literature | Real *patterns*, paraphrased |

### Synthetic data (generated, labelled as such)

- **Domain training corpus (~1,300 rows).** LLM-generated *before the hackathon*, prompted per
  domain for varied phrasing, register, and code-mixed Hindi-English, then hand-reviewed for
  label noise. Committed as CSV. Generated offline → no API dependency at demo time.
- **Field-intensity corpus (~250 rows)**, three classes, same method.
- **Demo challenge corpus (~40 rows)** including three deliberate near-duplicate clusters (7,
  4, and 3 members) with realistic phrasing variation across Hindi and English, plus edge
  cases the demo deliberately shows: one *below* the merge threshold that a validator must
  reject, one ambiguous domain, one remote/analytical problem to contrast geography behaviour.

> **The near-duplicate cluster must not be synthetically easy.** If the seven reports are
> paraphrases of one sentence, the dedup demo proves nothing and a sharp judge will see it.
> They must differ in vocabulary, length, language, and detail — one mentions iron staining,
> another only "dirty water", a third is in Hindi, a fourth is a field assistant's terse
> note. Getting these seven records right is worth more than an extra feature.

### Seeded institutional data — and the honesty mechanism

`seed/institutions.json` — 25 institutions (15 universities/labs, 10 industry/CSR/government).
Every record carries a **`data_provenance`** object:

```json
"data_provenance": { "identity": "PUBLIC_VERIFIED", "departments": "PUBLIC_VERIFIED",
                     "capabilities": "ESTIMATED_DEMO", "faculty": "SYNTHETIC_DEMO" }
```

Institution names, districts, coordinates and department names are **real and checkable**.
Capability strengths, project counts, student numbers and all faculty entries are **demo
estimates**, and the UI renders a provenance badge saying so. Two fictional entries
(JalTech Sensors, AgriSetu Analytics) exist to demonstrate startup/MSME matching and are
labelled fictional in the interface.

**This turns the biggest credibility risk into a credibility asset.** When a judge asks
*"is this data real?"* — and they will — the answer is a field in the schema and a badge on
the screen, not a scramble.

### Warm start — how the fake becomes real

The estimated fields are exactly the fields a **one-page institution self-registration form**
collects: departments, capabilities (checkbox against the 30-code taxonomy), facilities,
capacity, contact. No schema change, no migration. A state can bootstrap 200 institutions in
a week through the university coordinator role, and the `data_provenance` flags flip from
`ESTIMATED_DEMO` to `SELF_DECLARED` to `VERIFIED` as evidence arrives.

### User-generated data — the flywheel

| Signal | Accumulates from | Improves |
|---|---|---|
| Validator corrections of AI domain | Every validation | Domain classifier: append `(text, corrected_label)` and retrain in 4 s. **Active learning, free** |
| Merge confirm / reject | Every merge decision | Dedup threshold: tune to observed precision/recall instead of a guess |
| Match accept / decline **+ reason** | Every routing | Match weights: the decline reason (*"no lab capacity"* / *"too far"* / *"wrong domain"*) maps directly onto a component. Fit weights to real preferences with ~200 decisions |
| Project completion rate by institution × domain | Every project | `track_record` becomes measured rather than seeded |
| Verified impact per solution | Every pilot | `solution_precedent` in Tractability |

**The honest framing for judges:** *"Today the weights are informed defaults, and we show you
exactly where they live and who can change them. After 200 real match decisions, they are
fitted to observed institutional behaviour. The architecture does not change — only the
source of the numbers."* A system that is explicit about its cold-start state and has a
concrete path out of it is far stronger than one claiming accuracy it cannot have.

---

## 11. Database Schema

Full DDL: [`docs/schema.sql`](schema.sql) — 30 tables, tiered by build order.

### Tier 1 — must exist by hour 4 (13 tables)

`users` · `admin_areas` · `institutions` · `institution_units` · `capability_taxonomy` ·
`institution_capabilities` · `institution_metrics` · `challenges` · `challenge_media` ·
`clusters` · `cluster_members` · `scoring_weights` · `score_components` ·
`challenge_requirements`

### Tier 2 — full demo, hours 8–14 (10 tables)

`match_runs` · `match_recommendations` · `projects` · `project_partners` · `project_members` ·
`milestones` · `impact_indicators` · `outcomes` · `notifications` · `audit_log`

### Tier 3 — seeded, no UI (7 tables)

`themes` · `solutions` · `replication_suggestions` · `pilots` · `faculty`

### Six design decisions worth defending

1. **`institution_units` is one table for departments, centres and labs.** Expertise matching
   is then a single vector query instead of a three-way union. Nothing is lost — `kind`
   preserves the distinction where it matters (research components weight centres higher).
2. **AI output and human override live in the same row**, distinguished by a `*_source`
   column (`domain` + `domain_source ∈ {AI,HUMAN}`). Separate tables would double every read
   path for a field that is overridden perhaps 15% of the time.
3. **`score_components` persists the decomposition, not just the total.** The UI draws the
   waterfall without recomputing, and an officer six months later can see exactly why
   something ranked where it did — under which `weights_version`.
4. **`scoring_weights` is versioned and `is_active`-flagged**, never mutated. Changing weights
   creates a version. Historical scores stay reproducible.
5. **`cluster_members.method`** distinguishes `AUTO_SUGGEST` from `HUMAN` from `SEED`. This is
   the audit trail proving the system never auto-merged anything.
6. **`outcomes.verified_by` nullable** is the entire anti-gaming design: `NULL` means claimed,
   non-null means verified, and the dashboard reports the two as **separate numbers**.

**Indexes that matter:** HNSW cosine on `challenges.embedding`, `clusters.centroid`,
`institution_units.embedding`, `solutions.embedding`; btree on `challenges(status, domain)`
and `(lat,lng)`; `audit_log(entity, entity_id, at DESC)`.

**SQLite fallback:** every `vector(384)` becomes `TEXT` holding a JSON array, and similarity
moves to in-process numpy. Nothing else changes. Keep this switch *tested* — venue Postgres
has died before.

---

## 12. System Architecture

**One modular monolith. Two processes. One compose file.**

```
┌──────────────────────────────────────────────────────────────────┐
│  Next.js 15 (App Router, TS, Tailwind, shadcn/ui)                │
│  /citizen  /validator  /university  /industry  /gov              │
│  MapLibre GL + OSM raster tiles · Recharts · RHF + Zod           │
└───────────────────────────┬──────────────────────────────────────┘
                            │ REST + JSON, JWT bearer
┌───────────────────────────▼──────────────────────────────────────┐
│  FastAPI (single process, Python 3.11)                           │
│  ├── routers/    auth challenges clusters match projects gov     │
│  ├── services/   validation · lifecycle state machine · scoring  │
│  ├── ai/         embed · classify · dedupe · prioritise · match  │
│  │               · consortium · explain      ← model loaded ONCE │
│  └── db/         SQLModel + Alembic                              │
│  Static /media served by StaticFiles                             │
└───────────────────────────┬──────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│  PostgreSQL 16 + pgvector          (docker volume)               │
└──────────────────────────────────────────────────────────────────┘
```

**Why the AI is in-process, not a separate service.** It removes an entire integration
boundary — no second Dockerfile, no HTTP hop, no serialisation of 384-float arrays, no
"which service is down" at 4am. It saves roughly two hours, which is 8% of the budget. The
`ai/` package exposes pure functions with no FastAPI imports, so extracting it into its own
service later is a mechanical change. **This is the single highest-leverage architecture
decision in the plan.**

- **Async:** FastAPI `BackgroundTasks` only. **No Celery, no Redis, no broker.** The one
  genuinely slow path (batch re-clustering) is a button, not a queue.
- **Auth:** JWT, `python-jose` + `passlib[bcrypt]`, role claim in the token, dependency-injected
  role guards. Seeded demo accounts, one-click role switcher visible only when `DEMO_MODE=1`.
- **Storage:** local disk volume at `/media`, `uuid4` filenames, sha256 stored for free
  re-upload dedup. MinIO/S3 documented for scale, **not built**.
- **Maps:** MapLibre GL + OpenStreetMap raster tiles. **No API key, no billing, no quota.**
  Google Maps would add a signup, a key in env, a billing account, and a hard dependency on
  the venue network. Challenges are `(lat, lng)` + `admin_area_id`; the dashboard renders
  district choropleth + cluster markers sized by priority.
- **Notifications:** rows in `notifications` + an in-app bell. Email is **logged to a visible
  console pane, not sent**. We say this out loud in the demo — claiming SMTP that is not
  wired is a needless lie a judge may test.
- **Deployment:** `docker compose up` → three containers. **The demo runs on localhost.**
  A Render/Railway deploy exists only as a backup link on the slide. Assume the venue Wi-Fi
  fails, because it does.

---

## 13. API Architecture

Full contract with examples: [`docs/api-contract.md`](api-contract.md).

```
POST   /api/auth/login                      → {token, role, institution_id?}
POST   /api/auth/register

POST   /api/challenges                      submit + SYNCHRONOUS AI analysis (~90 ms)
GET    /api/challenges/{id}                 citizen status view with full journey
POST   /api/challenges/{id}/media           multipart evidence upload
GET    /api/challenges/{id}/duplicates      ranked candidates + score decomposition

GET    /api/validator/queue                 district queue, priority-ordered
POST   /api/validator/challenges/{id}/validate
POST   /api/validator/clusters/{id}/merge   {challenge_ids[]}  → audited, reversible
POST   /api/validator/clusters/{id}/split

GET    /api/clusters/{id}                   cluster + members + scores + requirements
GET    /api/clusters/{id}/score             component waterfall, exact contributions
POST   /api/clusters/{id}/rescore           re-run with a candidate weights version
GET    /api/clusters/{id}/matches           lead + collaborator + industry + consortium
POST   /api/clusters/{id}/matches/recompute

POST   /api/matches/{id}/respond            {accept|decline, reason}   ← the learning signal
POST   /api/projects                        created on acceptance
POST   /api/projects/{id}/team
POST   /api/projects/{id}/proposal
POST   /api/projects/{id}/transition        {to_status}  → state machine guard
POST   /api/projects/{id}/milestones/{n}/complete
POST   /api/projects/{id}/outcomes          baseline / endline + evidence

GET    /api/gov/dashboard                   KPI strip, funnel, distributions
GET    /api/gov/map                         GeoJSON: clusters + projects + pilots
GET    /api/gov/quadrant                    priority × tractability scatter
GET    /api/gov/coverage-gap                under-reporting districts (equity panel)
PUT    /api/gov/weights                     new weights version + activate (audited)

GET    /api/notifications
POST   /api/demo/reset                      DEMO_MODE only — restores seed state
```

**Three API decisions worth defending:**

1. **`POST /api/challenges` runs the AI pipeline synchronously.** The whole pipeline is ~90 ms;
   making it async would add a job table, a polling endpoint, and a spinner — cost with no
   benefit at this scale. The citizen sees the analysis *as the page settles*, which is a
   genuinely better product **and** the strongest 5 seconds of the demo. At real scale it
   moves behind a queue; the endpoint contract does not change.
2. **`/matches/{id}/respond` requires a `reason` on decline.** It is the highest-value
   training signal in the system (Section 10) and costs one enum field.
3. **`POST /api/demo/reset`.** Judging runs are unforgiving; a one-click restore to seed state
   means a fumbled click does not end the demo. Gated behind `DEMO_MODE`.

---

## 14. User Flows

**Citizen.** Open (no login needed to browse) → submit: title, description (voice-to-text via
browser API where available), photo, **map pin auto-filled from GPS** → *sees the AI analysis
card immediately*: domain, capabilities needed, "3 similar reports nearby — is this the same
issue?" → confirms or says no → gets a tracking link → status page shows the whole journey:
*Submitted → Validated → Merged into a cluster of 7 → Priority 66.5 → Matched to BAU + BIT
Mesra + CCL → Project active → Prototype → Pilot running in your block → Impact measured*.
Endline: citizen confirms the improvement. **This screen is the emotional payload of the
demo** — a citizen watching their complaint become an engineering project.

**Field assistant.** Same form + `on_behalf_of` (name, phone, household) and an offline draft
queue. The equity lever: without it the platform hears only from people who already have a voice.

**Government validator.** Queue sorted by priority, filtered to district → open a challenge:
raw text, photos with EXIF geo, AI analysis, **duplicate panel side-by-side with the score
decomposition** → actions: validate · edit any AI field (recorded as `HUMAN` source) ·
confirm/reject merge · split · reject with reason · route to grievance system (explicitly
"this is a repair order, not an innovation problem") → validated clusters flow to matching.

**AI engine** (no UI, invoked at three points). *On submit:* embed → classify domain →
extract capabilities → field intensity → duplicate search → return inline. *On validation:*
recompute cluster centroid, priority, tractability, theme assignment. *On match request:*
score every institution, split into two tracks, assign industry roles, run set cover, render
explanations. Each step writes `score_components` / `match_recommendations` so nothing is
recomputed for display.

**University.** Coordinator dashboard: *invited* challenges (with the full explanation of why
their institution) + a browsable open board → open a challenge: cluster detail, citizen
evidence, capability requirements, **their own capability gaps**, proposed consortium
partners, **auto-generated capstone brief with credit mapping** → Accept / Decline (+reason)
→ on accept, a project is created → form team (faculty mentor + students by discipline) →
submit proposal (approach, methodology, TRL start/target, timeline, budget) → milestones.

**Industry.** Open board filtered by sector and CSR theme, plus direct invitations with a role
already proposed → express interest → commit concretely (`{funding_inr, mentors, equipment,
pilot_site}`) → appear on the project as a partner with that role.

**Project team.** Proposal approved → milestone plan (seeded default per domain, editable) →
upload deliverables → faculty verifies → status transitions Development → Prototype → Field
Testing → Pilot → Completed → record endline outcomes → **solution published to the registry**.

**Government (admin).** Portfolio dashboard → priority × tractability quadrant → weight
sliders (audited) → coverage-gap panel → pilot permission → stalled-project alerts →
replication suggestions from the registry.

---

## 15. Project Lifecycle

```
SUBMITTED ─validator confirms real──────────────► UNDER_REVIEW
UNDER_REVIEW ─metadata set, not duplicate───────► VALIDATED
             └─duplicate confirmed──────────────► MERGED  (into cluster; never closed)
             └─not a societal challenge─────────► REJECTED / ROUTED_TO_GRIEVANCE
VALIDATED ─priority computed, match run─────────► MATCHED
MATCHED ─university coordinator accepts─────────► INSTITUTION_ACCEPTED
        └─all invited decline───────────────────► back to MATCHED, widen radius, notify gov
INSTITUTION_ACCEPTED ─faculty + ≥1 student──────► TEAM_FORMED
TEAM_FORMED ─proposal submitted─────────────────► PROPOSAL_SUBMITTED
PROPOSAL_SUBMITTED ─validator/gov approves──────► APPROVED
APPROVED ─first milestone started───────────────► DEVELOPMENT
DEVELOPMENT ─prototype milestone verified───────► PROTOTYPE
PROTOTYPE ─deployed at site, data collected─────► FIELD_TESTING
FIELD_TESTING ─gov grants pilot permission──────► PILOT
PILOT ─all milestones verified──────────────────► COMPLETED
COMPLETED ─endline recorded AND verified────────► IMPACT_MEASURED ──► SOLUTION REGISTRY
any state ─no activity 60 days──────────────────► STALLED (gov alert)
```

**Three transitions carry the design:**
- **`MERGED` never means closed.** The report becomes evidence and *raises* cluster priority.
- **`FIELD_TESTING → PILOT` requires government permission.** This is where the state's real
  authority sits, and modelling it correctly is what makes the workflow believable to an
  official. A platform that lets a student team declare a pilot is a platform no district
  will adopt.
- **`COMPLETED → IMPACT_MEASURED` requires a *verified* endline.** Projects can complete
  without proving impact — and the dashboard shows that gap honestly rather than hiding it.

**Guards are enforced server-side** in `services/lifecycle.py` as an explicit transition
table. The UI only offers legal transitions; the API rejects illegal ones regardless.

---

## 16. Demo Scenario

Full minute-by-minute run sheet: [`docs/01-demo-script.md`](01-demo-script.md).

**The story:** *Torpa block, Khunti district. Hand pumps fail, nobody knows when, the block
mechanic covers hundreds of them, and the water that does come is iron-stained. Families walk
two kilometres. Children miss school fetching water.*

That framing matters: the real failure is **not** "a pump broke" — it is that **no one knows
it broke** and there is no maintenance system. A repair order fixes one pump. An engineering
project fixes the maintenance system. **That distinction is the entire product**, dramatised
in one story.

Seven acts, ~7 minutes: submit (live, in Hindi) → AI analysis appears → duplicates detected →
validator merges, priority visibly jumps 41 → 66.5 → the two-track routing screen with IIT
Madras at 1,230 km topping the collaborator list → consortium assembles, coverage 30% → 87%
→ university accepts, team forms, project advances → government dashboard, verified impact,
replication offered to 7 other clusters.

**Closing line:** *"A citizen said the water is dirty. Eleven minutes later, four institutions
across 1,200 kilometres had a scoped project with a named team. That is the gap this platform
closes."*

---

## 17. Tech Stack

| Layer | Choice | Why this | Do we need it? | 24h-realistic? |
|---|---|---|---|---|
| Frontend | **Next.js 15 + TS** | App Router gives file-based routing for 5 role portals free; API routes as an escape hatch | Yes | Yes if ≥2 people know React. **If not, Vite + React Router** — do not learn a framework tonight |
| Styling | **Tailwind + shadcn/ui** | Copy-paste components, no design system to invent. Biggest single UI accelerator | Yes | Yes |
| Charts | **Recharts** | Declarative React, covers bar/line/scatter/funnel | Yes | Yes |
| Maps | **MapLibre GL + OSM tiles** | **No API key, no billing, no quota**; Google Maps adds a network dependency at demo time | Yes | Yes |
| Forms | **React Hook Form + Zod** | One schema validates client and mirrors the Pydantic model | Yes | Yes |
| Backend | **FastAPI** | Same language as the AI ⇒ no service boundary. Auto OpenAPI ⇒ generated TS types ⇒ frontend unblocked at hour 2 | Yes | Yes |
| ORM | **SQLModel + Alembic** | SQLModel = SQLAlchemy + Pydantic in one class definition | Yes | Yes |
| DB | **Postgres 16 + pgvector** | Vectors and relations in one store. No separate vector DB to run | Yes | Yes |
| Embeddings | **paraphrase-multilingual-MiniLM-L12-v2** | 384-d, CPU, ~20 ms, Hindi+English in one space | Yes — it is the product | Yes. **Bake into the image** |
| ML | **scikit-learn** (LogisticRegression, AgglomerativeClustering) | Trains in seconds, artifacts are KB, fully interpretable | Yes | Yes |
| Auth | **python-jose + passlib[bcrypt]** | Stateless JWT, no session store | Yes | Yes |
| Deploy | **docker compose** | One command, three containers, runs offline | Yes | Yes |

**Deliberately absent:** Redis · Celery · Kafka · Elasticsearch · Kubernetes · a separate
vector DB · GraphQL · a native mobile app · any LLM on the critical path.

**The one optional LLM.** `LLM_ASSIST=on` enables (a) structured field extraction from rambling
text and (b) a narrative cluster summary. Both have deterministic fallbacks; both are off the
critical path; **the demo runs with it off**. If asked why we do not use an LLM for
classification: *latency, cost, network dependency at a venue, non-determinism during
judging, and — most importantly — a 40 KB logistic regression we can fully explain beats a
black box we cannot, for a government decision-support system.*

---

## 18. Team Division

Six people, six tracks, contract-first so they merge late without collision.

| # | Track | Owns | Ships by |
|---|---|---|---|
| **A** | Frontend — citizen + shell | Design system, auth shell, role switcher, submission form, map pin, AI analysis card, citizen status tracker | H10 |
| **B** | Frontend — government | KPI strip, funnel, MapLibre district layer, domain/district charts, **weight sliders**, **quadrant scatter**, coverage gap | H14 |
| **C** | Full-stack — institutions | University portal (invitation → accept → team → proposal), industry portal, project + milestone UI, lifecycle transitions | H14 |
| **D** | Backend lead | Schema, Alembic, auth, all CRUD, validator endpoints, lifecycle state machine, seed loader | H12 |
| **E** | AI/ML | `ai/` package: embeddings, classifiers, dedup, scoring, matching, consortium, explanations. **Pure functions, no FastAPI imports** | H12 |
| **F** | Integration / DevOps / demo | docker-compose, seed corpus authoring, E2E test script, deployment, **demo script and rehearsal**, slides. Floats to whoever is behind | continuous |

**The three rules that make late merging work:**

1. **Contract first, by hour 2.** D publishes the OpenAPI stub with hardcoded example responses.
   A/B/C generate TS types and build against MSW mocks. Nobody blocks on anybody.
2. **E's code imports nothing from the web layer.** `ai/` takes dicts and returns dicts.
   D wraps it. This means E can develop and test entirely offline with `python -m ai.demo`,
   and the AI is testable without the API running.
3. **F owns `main` and is the only person who merges.** Everyone else works on
   `track-a/…`, `track-e/…`. `main` must be demoable at every hour.

**Pairing rule:** at hour 15, whoever is ahead pairs with whoever is behind. The demo depends
on the *slowest* track, so individual heroics on a finished track are worth nothing.

---

## 19. 24-Hour Execution Plan

Detailed hour-by-hour with checkpoints: [`docs/02-execution-plan.md`](02-execution-plan.md).

| Phase | Hours | Outcome | Gate |
|---|---|---|---|
| 0 · Lock | 0–2 | Scope frozen, **demo script written first**, schema agreed, OpenAPI stub published, compose up, repo scaffolded | Everyone can run `docker compose up` |
| 1 · Foundations | 2–6 | Auth + Tier-1 tables + seed loaded; embeddings live; domain classifier trained; citizen form posts | **A citizen submission is stored with an embedding** |
| 2 · Intelligence | 4–9 | Dedup + priority + explanations; validator console; citizen status page | **Submit → duplicate suggested → merge → priority changes** |
| 3 · Matching | 8–12 | Two-track matching + industry roles + consortium; university portal accept→team→proposal | **Cluster → consortium with explanations on screen** |
| 4 · Lifecycle + dashboards | 9–15 | Projects, milestones, transitions; government dashboard, map, quadrant, sliders | **Government dashboard shows real seeded data** |
| 5 · **Integration freeze #1** | 15–17 | Everything on `main`; full E2E path runs end to end; contract mismatches fixed | **The seven-act demo runs once, unassisted** |
| 6 · Should-build | 17–19 | Replication engine, notifications, capstone brief, Hindi path — *only if act 5 passed* | Nothing half-built survives to 19 |
| 7 · Demo hardening | 19–21 | Seed corpus curation, empty/error/loading states, mobile check, **rehearsal #1**, backup video recorded | **FEATURE FREEZE at H20** |
| 8 · Bugfix only | 21–23 | Blocker bugs only. Offline verification (Wi-Fi off). Deployment + backup link | Demo runs with the network disabled |
| 9 · Rehearse | 23–24 | Rehearsals #2 and #3, slides final, Q&A drill on the objections in §23 | Every member can run the demo alone |

**Standing rules:** commit every 30 minutes · no new dependencies after H12 · `main` demoable
at all times · **feature freeze H20, no exceptions** · sleep in shifts (a mistake at hour 21
costs more than the feature gained at hour 4).

**Deliberate overlaps** — Phase 2 starts at H4 while Phase 1 finishes at H6, because E only
needs the embedding function (H4), not finished CRUD. Same for Phase 4 at H9. Serialising
these wastes ~3 hours.

**Prepared before the clock starts** (legitimate, and everyone does it): the synthetic training
corpora, the seeded institution profiles, the repo scaffold, the docker image with the model
baked in. Building those during the 24 hours is a waste of the 24 hours.

---

## 20. Feature Prioritisation

| Feature | Impact | Demo value | Difficulty | AI depth | MVP? |
|---|---|---|---|---|---|
| Citizen submission + evidence + geo | High | High | Low | — | **YES** |
| **Live AI analysis on submit** | High | **Very high** | Medium | High | **YES** |
| Domain classification | High | Medium | Low | Medium | **YES** |
| **Dedup + clustering + merge** | **Very high** | **Very high** | Medium | **High** | **YES** |
| **Priority + waterfall + live sliders** | **Very high** | **Very high** | Low | Medium | **YES** |
| Field intensity | High | Medium | Low | Medium | **YES** |
| **Two-track university matching** | **Very high** | **Very high** | Medium | **Very high** | **YES** |
| Industry role matching | High | High | Medium | High | **YES** |
| **Consortium Builder** | **Very high** | **Very high** | Medium | **Very high** | **YES** |
| Explanations everywhere | High | **Very high** | Low | Medium | **YES** |
| Validator console | High | High | Medium | — | **YES** |
| University accept → team → proposal | High | High | Medium | — | **YES** |
| Project lifecycle + milestones | High | High | Medium | — | **YES** |
| Government dashboard + map | High | **Very high** | Medium | — | **YES** |
| **Priority × tractability quadrant** | High | High | Low | Medium | **YES** |
| Citizen status tracker | Medium | **Very high** | Low | — | **YES** |
| Solution registry + replication | **Very high** | High | Medium | High | SHOULD |
| Capstone brief generation | High | High | **Low** | Low | SHOULD |
| Hindi end-to-end | High | High | Low | — | SHOULD |
| Industry self-service portal | Medium | Medium | Medium | — | SHOULD |
| Impact baseline/endline capture | High | Medium | Low | — | SHOULD |
| Notifications | Low | Low | Low | — | SHOULD |
| Theme detection (level 2) | High | Medium | Low | Medium | SHOULD |
| Coverage-gap equity panel | Medium | Medium | Low | Low | SHOULD |
| Audit log viewer | Low | Low | Low | — | CUT |
| Proposal document editor | Low | Low | High | — | CUT |
| PDF export | Low | Low | Medium | — | CUT |
| Real email/SMS | Low | Low | Medium | — | CUT |
| Faculty self-registration | Low | Low | Medium | — | CUT |
| Chat / comments | Low | Low | Medium | — | CUT |

### The five that absolutely must work

1. **Dedup + merge with visible priority change** — proves aggregation, the core insight.
2. **Two-track matching with the geography split** — the single most differentiating screen.
3. **Consortium Builder with capability-gap reasoning** — proves team assembly, not routing.
4. **Explanations attached to every recommendation** — converts "AI" from claim to demonstration.
5. **Citizen status tracker showing the full journey** — proves the pipeline end to end and
   lands emotionally.

If only these five work, the demo still wins. If the other twenty work and one of these does
not, it does not.

### Cut order when time runs short (top = cut first)

audit log viewer → PDF export → proposal editor → notifications → industry self-service →
coverage-gap panel → impact capture forms (seed the numbers instead) → theme detection →
Hindi (keep the *model*, drop the UI toggle) → replication engine → **stop. Everything below
this line is one of the five.**

---

## 21. Risks & Mitigations

| # | Risk | Likelihood | Blast radius | Mitigation |
|---|---|---|---|---|
| 1 | **Domain classifier misfires live** | Medium | Demo credibility | Validator can override *any* AI field on screen — the override **is** the story ("human in the loop"). Confidence shown; below 0.55 the UI says "low confidence, needs review" instead of asserting. Seeded demo challenges are pre-verified to classify correctly |
| 2 | **Similarity mis-calibration silently kills semantic weights** | **High** — we hit it while writing the reference implementation | Matching becomes headcount-ranking | Fixed affine calibration with p5/p95 anchors, derived from the real encoder at hour 6. **Acceptance test at hour 12:** hand-label the correct lead for 12 challenges, require top-1 ≥ 7/12 and top-3 ≥ 11/12. If it fails, fix the anchors before touching the weights |
| 3 | **Model download fails at the venue** | Medium | **Total demo failure** | Bake the model into the Docker image; `HF_HUB_OFFLINE=1`; verify in airplane mode at hour 22. Non-negotiable |
| 4 | **Wrong university recommended, judge notices** | Medium | Credibility | Never present one answer — present a ranked list with contributions and a "why not #2". Frame as *decision support*: the coordinator accepts or declines with a reason, and that reason is training data. A system that says "here is my reasoning, correct me" is stronger than one claiming to be right |
| 5 | **"Your institutional data is fake"** | **High — expect it** | Credibility | `data_provenance` in the schema and a badge in the UI. Real names/departments, labelled estimates, two clearly-fictional companies. Answer with the warm-start form (Section 10). **Prepared honesty beats a scramble** |
| 6 | **Dedup false-merge suppresses a real problem** | Medium | Ethical + design | Structurally impossible to suppress: no auto-merge, merges are audited and reversible, and merging *raises* priority rather than closing anything. Two thresholds with a human-reviewed grey band |
| 7 | **Dedup false-negative — duplicates stay split** | Medium | Weakened story | Lower-cost failure than #6 and deliberately preferred. The re-cluster button catches them in batch |
| 8 | **Unrealistic government workflow, official in the panel objects** | Medium | Fatal with a domain judge | Government is validator/prioritiser/procurer, **never project manager**. Pilot permission is an explicit gated transition. "Route to grievance system" exists as a first-class outcome — we say what we are *not* |
| 9 | **Scope explosion** | **High — the default failure** | Everything | 5 must-work features (§20), a written cut order, feature freeze at H20, `main` demoable hourly, F holds the line and is empowered to say no |
| 10 | **Internet/API dependency** | Medium | Demo failure | No LLM on the critical path. OSM tiles cached. Everything runs on localhost. Wi-Fi-off rehearsal at hour 22 |
| 11 | **Deployment fails during judging** | Medium | Demo failure | Localhost is primary, cloud is backup. Plus a **recorded full-run video** on a local drive. Three fallbacks deep |
| 12 | **Bad UX under demo pressure** | Medium | Score | Rehearse 3×; every member can run it solo; `POST /api/demo/reset`; seeded state means no live typing beyond one form; empty and error states built at hour 19 |
| 13 | **Empty dashboards look like a broken product** | **High if unaddressed** | Score | Seed ~40 challenges, 12 clusters, 6 projects at varied lifecycle stages, 2 completed with verified impact. **A dashboard of zeroes reads as a failed build**, even when it is a correct one |
| 14 | **Postgres/pgvector won't start on the demo machine** | Low | Total | Tested SQLite + numpy fallback behind one env var. Test it at hour 18, not hour 23 |
| 15 | **Merge conflicts at integration** | Medium | Hours lost | Contract-first at H2, generated types, one merger (F), 30-minute commits, integration freeze at H15 rather than H22 |
| 16 | **Equity bias — only urban/literate citizens submit** | Real product risk | Legitimacy | `FIELD_ASSISTANT` role; vulnerability weight in priority; coverage-gap panel that flags under-reporting districts. **Naming this risk unprompted is itself a credibility signal** |

---

## 22. Final Architecture

```
        CITIZEN            FIELD ASSISTANT          GRIEVANCE IMPORT
       (web, Hindi)        (on-behalf-of)           (adapter, seeded)
            └───────────────────┴───────────────────────┘
                                ▼
            ┌───────────────────────────────────────┐
            │  CHALLENGE INTAKE                     │
            │  text · photo (EXIF) · GPS · language │
            └───────────────────┬───────────────────┘
                                ▼
            ┌───────────────────────────────────────┐
            │  AI PROCESSING LAYER  (~90 ms, local) │
            │  ┌─────────────────────────────────┐  │
            │  │ SHARED EMBEDDING  384-d MiniLM  │  │
            │  └────┬───────┬───────┬───────┬────┘  │
            │  domain  capability  field    dup     │
            │  classify extract   intensity search  │
            └───────────────────┬───────────────────┘
                                ▼
            ┌───────────────────────────────────────┐
            │  VALIDATION  (human, always)          │
            │  confirm · severity · merge/split ·   │
            │  override any AI field · or route out │
            └───────────────────┬───────────────────┘
                                ▼
            ┌───────────────────────────────────────┐
            │  CLUSTER & SCORE                      │
            │  incident → cluster → systemic theme  │
            │  priority(7) × tractability(4)        │
            │  → triage quadrant                    │
            └───────────────────┬───────────────────┘
                                ▼
            ┌───────────────────────────────────────┐
            │  MATCHING & CONSORTIUM                │
            │  LEAD track ‖ COLLABORATOR track      │
            │  industry role assignment             │
            │  greedy set cover over capabilities   │
            │  exact contribution explanations      │
            └───────────────────┬───────────────────┘
                                ▼
     ┌──────────────────────────┼──────────────────────────┐
     ▼                          ▼                          ▼
 UNIVERSITY                 INDUSTRY                  GOVERNMENT
 accept · team ·      mentor · fund · fabricate ·   approve · permit
 proposal             host pilot · deploy            pilot · procure
     └──────────────────────────┼──────────────────────────┘
                                ▼
            ┌───────────────────────────────────────┐
            │  PROJECT LIFECYCLE                    │
            │  milestones · deliverables · TRL      │
            └───────────────────┬───────────────────┘
                                ▼
                    PROTOTYPE → FIELD TESTING → PILOT
                                ▼
            ┌───────────────────────────────────────┐
            │  IMPACT MEASUREMENT                   │
            │  baseline → endline · claimed vs      │
            │  VERIFIED (separate numbers)          │
            └───────────────────┬───────────────────┘
                                ▼
            ┌───────────────────────────────────────┐
            │  SOLUTION REGISTRY                    │
            │  embed solution → find matching open  │
            │  clusters → propose replication ──────┼──┐
            └───────────────────┬───────────────────┘  │
                                ▼                      │
            ┌───────────────────────────────────────┐  │
            │  GOVERNMENT ANALYTICS                 │  │
            │  quadrant · funnel · map · coverage   │  │
            │  gap · weight control (audited)       │  │
            └───────────────────────────────────────┘  │
                                                        │
      ◄──────────── LOOP CLOSES ────────────────────────┘
      replication re-enters as pre-matched clusters
```

### How data actually moves

1. **Intake.** Text normalised → embedded once (384-d). That vector is written to
   `challenges.embedding` and **never recomputed**. Domain, capabilities and field intensity
   are three cheap heads over the same vector; the duplicate search is an HNSW query over
   `challenges.embedding` blocked by domain, radius `3·d₀`, and 180 days.
2. **Validation.** A human confirms or overrides. Overrides set `domain_source='HUMAN'` and
   append to the retraining corpus. Confirming a merge writes `cluster_members` with
   `method='HUMAN'` and the officer's id.
3. **Cluster.** The centroid is the mean of member embeddings, re-normalised on each merge.
   Priority and tractability compute from `ClusterFacts`; **every component is persisted** to
   `score_components` with its `weights_version`, so the waterfall renders without recompute
   and stays reproducible when weights change later.
4. **Match.** Cluster centroid is compared against `institution_units.embedding` (HNSW).
   Capability coverage is a join through `challenge_requirements` × `institution_capabilities`.
   Distance is haversine from the cluster centroid. Two tracks are produced from **the same
   `Base`** — only the geo multiplier differs. Consortium runs greedy set cover over the
   union of both tracks plus industry. Everything lands in `match_recommendations` with
   `components` and `contributions` as JSONB, so the UI never recomputes a score.
5. **Collaboration.** Acceptance creates a `project`, copies partners, seeds milestones from
   a per-domain template. `institution_metrics.active_projects` increments — feeding straight
   back into the `capacity` component of future matches. **The system learns institutional
   load without anyone entering it.**
6. **Impact.** Baseline is captured at `APPROVED`, endline at `COMPLETED`. Verification sets
   `outcomes.verified_by`; the dashboard aggregates claimed and verified separately.
7. **Registry and loop.** On `IMPACT_MEASURED`, the solution is embedded and stored. A cosine
   query against open cluster centroids produces replication suggestions — which enter the
   pipeline **already matched**, skipping steps 4 and 5. That is the compounding return, and
   it is why the architecture is a loop rather than a funnel.

---

## 23. Pitch / Judging Strategy

### The 30-second frame

> *"India does not have a problem-reporting shortage. It has a problem-**matching** shortage.
> Forty-five thousand colleges must produce student projects anyway. District administrations
> have problems they cannot solve. Nothing connects them. Sahyog is that connection: it turns
> a citizen's report into a structured, prioritised, capability-tagged challenge, and then
> assembles the specific team of institutions that can actually solve it — with a written
> reason for every choice."*

### Where we score

| Criterion | Our strongest evidence |
|---|---|
| **Innovation** | Consortium set cover, field-intensity-conditional geography, two-track routing, replication loop. None of these exist in a grievance portal |
| **Social impact** | Vulnerability weighting, field-assistant role, coverage-gap panel, verified-impact requirement. Equity is designed in, not asserted |
| **AI/ML depth** | One shared embedding → five capabilities. A trained classifier with a reported held-out score *and* a stated synthetic-data caveat. Set cover. Exact linear attributions. **Calibration handled explicitly** |
| **Scalability** | pgvector HNSW to tens of millions; stateless API; matching is O(institutions) ≈ thousands; only embedding is heavy, and it is batched and cached |
| **Government usefulness** | Priority × tractability quadrant, tunable audited weights, coverage gap, claimed-vs-verified impact. Answers *"what do we fund next"* with evidence |
| **Feasibility** | Runs on `docker compose up`, offline, on a laptop. Scoring engine is committed and runnable **today** |
| **Measurable outcomes** | Baseline/endline with verification, replication count, match-acceptance rate |

### Anticipated objections — and the answers

| Objection | Answer |
|---|---|
| *"This is a complaint portal with extra steps."* | Open the theme view: 200 reports, one systemic maintenance failure across 6 districts, one programme. Then the consortium screen. A complaint portal has no analogue for either. **Do not argue — show these two screens.** |
| *"Your AI is just cosine similarity."* | Cosine is one of five consumers of the embedding. Show the trained classifier's held-out score, the ablation against zero-shot, the greedy set cover, and the exact contribution decomposition. Then note we *chose* linear scoring for auditability |
| *"Is this data real?"* | Institution names, districts and departments: real and checkable. Capability strengths and faculty: labelled estimates, badged in the UI, `data_provenance` in the schema. Here is the self-registration form that replaces them. **Answering this crisply wins more points than the feature it concerns** |
| *"Universities will never participate."* | Show the capstone brief with NEP credit mapping. Universities need real problems more than the state needs students — the incentive already exists, the channel does not |
| *"Government already has CPGRAMS."* | We sit *above* grievance redressal and consume it: unresolved, recurring grievances are an input source (the import adapter). Repair orders route back out. We handle what grievance systems structurally cannot — problems needing R&D, not redressal |
| *"What if the AI merges away a real problem?"* | It cannot. No auto-merge, human confirmation, full audit, reversible, and a merge *raises* priority rather than closing anything. Show `cluster_members.method` |
| *"Why is a Chennai institute recommended for a Jharkhand village?"* | It is not — it is recommended as *remote technical collaborator*, and simultaneously ranks 8th as lead because geography removed half its score. **Show both columns on one screen.** This objection is a gift: it is exactly what the design anticipates |
| *"Will this work at state scale?"* | pgvector HNSW to tens of millions of vectors; embedding is the only heavy step and is batched; matching is O(institutions). The one real bottleneck is **human validators**, which is why priority ranking exists |
| *"You built this in 24 hours — what is missing?"* | Real email/SMS, DigiLocker auth, mobile app, fund disbursement, ASR for tribal languages, and **a real labelled dataset**. Naming these unprompted, with the warm-start path, reads as engineering maturity — not weakness |

### Three things to say out loud that most teams will not

1. **"We do not have a labelled dataset, and here is exactly what changes when we do."**
2. **"We chose a linear model over a better black box because a government system must be
   able to explain a decision to the person it affected."**
3. **"Email is not wired. It writes to a log. We are showing you what works."**

Judges have sat through many demos claiming everything works. Calibrated honesty is
differentiating, and it makes every *other* claim more believable.

### Do not

- Do not call it "AI-powered" without immediately showing a number.
- Do not demo a feature that failed in rehearsal. Cut it and never mention it.
- Do not read the slides. The product is the argument.
- Do not defend a bug. *"Known issue, here is the cause, here is the fix"* — then move on.
