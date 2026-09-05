# Training the Models — Setup Guide

Everything you need to lay out `C:\SIH` and train both classifiers, in order.

---

## 1. Folder structure

Create this layout and drop in the files sent to you in chat:

```
C:\SIH\
├── ai\
│   ├── __init__.py                     ← empty file, create it yourself
│   ├── scoring_reference.py
│   │
│   ├── models\
│   │   ├── __init__.py                 ← empty file, create it yourself
│   │   ├── dataprep.py
│   │   ├── embedder.py
│   │   ├── train_domain.py
│   │   ├── train_field.py
│   │   └── predict.py
│   │
│   ├── data\
│   │   ├── domain_train.csv            ← your 1,320-row file, RENAMED to this
│   │   └── field_intensity_train.csv   ← your 250-row file, RENAMED to this
│   │
│   └── artifacts\                      ← leave empty; scripts write here
│
├── seed\
│   ├── institutions.json
│   ├── capability_taxonomy.json
│   └── validate_seed.py
│
└── docs\
    └── ...                             ← the plan docs, optional for training
```

**Non-negotiable details:**

| Requirement | Why |
|---|---|
| `ai/__init__.py` and `ai/models/__init__.py` must exist and be **empty** | Without them, `from ai.models.x import y` fails — every script does this |
| CSVs renamed **exactly** to `domain_train.csv` / `field_intensity_train.csv` | The scripts hardcode these filenames inside `ai/data/` |
| `ai/artifacts/` folder exists (can be empty) | The training scripts write into it; some setups need the folder to pre-exist |
| Run everything from `C:\SIH` (the repo root), not from inside `ai/models/` | Scripts resolve paths relative to the repo root |

---

## 2. Install dependencies

Open PowerShell in `C:\SIH`:

```powershell
cd C:\SIH
python -m venv venv
venv\Scripts\activate
pip install scikit-learn joblib numpy
```

This is enough to train immediately using the **tfidf backend** — no download, no internet dependency, works right away.

### Optional: the real multilingual encoder

If you want the actual transformer model instead of the tfidf fallback:

```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
```

CPU-only torch is a few hundred MB. The encoder weights (`paraphrase-multilingual-MiniLM-L12-v2`) download automatically on first use and cache locally afterward. This needs to reach `huggingface.co` — it failed in the sandbox this was built in because of a proxy block, but should work fine from your own machine.

---

## 3. Train — order matters

```powershell
cd C:\SIH
python ai\models\train_domain.py
python ai\models\train_field.py
```

**Run `train_domain.py` first, always.** `train_field.py` chains the domain classifier's output to build its domain-prior signal, and on the tfidf backend it reuses the encoder that `train_domain.py` already fitted. Running them in the other order silently degrades the field-intensity model's accuracy — it won't error, it'll just quietly score worse.

To use the real transformer instead of tfidf, set the backend first:

```powershell
$env:SOCIOSOLVE_BACKEND="transformer"
python ai\models\train_domain.py
python ai\models\train_field.py
```

(Without setting `SOCIOSOLVE_BACKEND`, both scripts default to `tfidf`.)

---

## 4. Verify it worked

```powershell
python ai\models\predict.py          # runs 3 sample challenges end-to-end
python ai\scoring_reference.py       # scoring math only, no ML deps needed
python seed\validate_seed.py         # checks institutions.json integrity
```

**What success looks like:**

- `ai\artifacts\domain_clf.joblib` appears (~19 KB)
- `ai\artifacts\field_clf.joblib` appears (~7 KB)
- `ai\artifacts\domain_metrics.json` and `field_metrics.json` appear, containing the macro-F1 scores
- `predict.py` prints domain + field-intensity predictions for 3 sample challenges without errors
- `validate_seed.py` reports `0 errors`

---

## 5. Expected numbers (tfidf backend, as measured)

| Model | Metric | Score |
|---|---|---|
| Domain classifier | macro-F1 (held-out) | **0.850** |
| Domain classifier | accuracy | 0.852 |
| Domain classifier | confidence-gate accuracy (≥0.55) | 0.967 |
| Field intensity | macro-F1 (blended) | **0.769** |
| Field intensity | monotonic check | passes (0.248 → 0.582 → 0.727) |

If your numbers are wildly different, something in the folder layout or run order is off — re-check steps 1 and 3 first.

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'ai'` | Running from the wrong directory, or missing `__init__.py` | Run from `C:\SIH`, confirm both empty `__init__.py` files exist |
| `FileNotFoundError: ai/data/domain_train.csv` | CSV not renamed / not in `ai/data/` | Check exact filename and location |
| field model's macro-F1 looks worse than 0.769 | Ran `train_field.py` before `train_domain.py` | Delete `ai\artifacts\*.joblib`, re-run in the correct order |
| `httpx.ProxyError` / connection errors on the transformer backend | Can't reach huggingface.co | Use `tfidf` backend instead (default), or check your network/proxy |
| Everything works but capability extraction returns nothing | Expected on the tfidf backend — it requires the real transformer | Switch to `SOCIOSOLVE_BACKEND=transformer`, or ignore for now (domain + field intensity still work fully on tfidf) |
