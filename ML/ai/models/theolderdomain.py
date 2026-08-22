"""
MODEL 2 of 3 - DOMAIN CLASSIFICATION.

    input   normalised challenge text (English / Hindi / Hinglish)
    output  1 of 11 domains + calibrated confidence + top-3 alternatives
    model   multinomial logistic regression over the 384-d shared embedding
    data    ai/data/domain_train.csv  (1320 rows, 11 x 120, 3 languages x 440)
    train   seconds on CPU
    infer   < 1 ms after the embedding
    artifact ai/artifacts/domain_clf.joblib  (tens of KB)

Run:
    python ai/models/train_domain.py                 # transformer encoder
    SAHYOG_BACKEND=tfidf python ai/models/train_domain.py    # offline baseline

WHY LOGISTIC REGRESSION AND NOT SOMETHING BIGGER
  Fine-tuning a transformer head would buy maybe 2-4 points of macro-F1 for
  hours of GPU time, a much larger artifact, and an unexplainable model. LR
  over a frozen encoder trains in seconds, ships as a ~40 KB file, and -
  the part that matters for a government system - its decision decomposes
  into per-feature contributions you can actually show someone.

  This is the same argument as the linear scoring model in
  ai/scoring_reference.py: we trade a few points of accuracy for
  auditability, on purpose, and we say so.

WHAT THIS SCRIPT REPORTS, AND WHY EACH NUMBER IS THERE
  macro-F1 held out    the headline. Macro not micro: the classes are
                       balanced here, but macro keeps us honest if real
                       submissions skew toward water and sanitation.
  per-language F1      the multilingual claim needs evidence. If Hindi F1
                       collapses, the encoder is not doing what we say.
  confusion matrix     shows WHICH pairs confuse. sanitation/water and
                       rural_livelihoods/agriculture are the ones to watch.
  confidence gate      the UI suppresses labels below 0.55. That threshold
                       is worthless unless you measure accuracy above and
                       below it - so we do.
  zero-shot baseline   the fallback that ships when the joblib is missing.
                       Also the ablation: trained-vs-zero-shot is the
                       evidence that training on synthetic data was worth it.
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ai.models.dataprep import DATA_DIR, prepare          # noqa: E402
from ai.models.embedder import Embedder, get_embedder     # noqa: E402

ARTIFACTS = Path(__file__).resolve().parent.parent / "artifacts"
MODEL_PATH = ARTIFACTS / "domain_clf.joblib"
METRICS_PATH = ARTIFACTS / "domain_metrics.json"

CONFIDENCE_GATE = 0.55      # below this the UI must say "needs review"

# Used by the zero-shot fallback. One sentence per domain, written to sit in
# the same semantic neighbourhood as a real report - deliberately concrete,
# because "education" as a bare word embeds near nothing useful.
DOMAIN_PROTOTYPES = {
    "education": "school teacher classroom students learning mid-day meal scholarship admission dropout",
    "healthcare": "hospital clinic doctor nurse medicine vaccine patient health centre ambulance treatment",
    "agriculture": "farmer crop soil irrigation seed fertiliser harvest pest mandi farming land",
    "water": "drinking water hand pump borewell pipeline tap supply well groundwater tank",
    "sanitation": "toilet drain sewage garbage waste cleaning open defecation soak pit sanitation",
    "environment": "pollution forest river tree air quality mining erosion wildlife environmental damage",
    "energy": "electricity power transformer solar street light grid outage voltage connection",
    "urban_infrastructure": "road pothole bridge drainage footpath traffic street municipal building construction",
    "accessibility": "disability wheelchair ramp accessible blind deaf divyang assistive impaired",
    "public_administration": "certificate application office portal government scheme document official record grievance",
    "rural_livelihoods": "employment wages MGNREGA self help group artisan livelihood income cooperative skill",
}


# ---------------------------------------------------------------------------
def build_features(rows, embedder):
    X = embedder.encode([r.text for r in rows], show_progress=False)
    y = np.array([r.label for r in rows])
    langs = np.array([r.language for r in rows])
    return X, y, langs


def zero_shot_predict(X, labels, embedder):
    """Fallback path - no training artifact required.

    Cosine of each text against a prototype embedding per domain. This is
    what serves when domain_clf.joblib is missing or fails to load, so the
    service degrades instead of 500-ing mid-demo. It is real code, not a
    sentence in a slide."""
    protos = embedder.encode([DOMAIN_PROTOTYPES[l] for l in labels])
    sims = X @ protos.T                       # both sides are L2-normalised
    return np.array([labels[i] for i in sims.argmax(1)]), sims


def macro_f1(y_true, y_pred, labels):
    f1s = []
    for l in labels:
        tp = int(((y_pred == l) & (y_true == l)).sum())
        fp = int(((y_pred == l) & (y_true != l)).sum())
        fn = int(((y_pred != l) & (y_true == l)).sum())
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * p * r / (p + r) if p + r else 0.0)
    return float(np.mean(f1s)), f1s


def main():
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GridSearchCV, StratifiedKFold
    import joblib

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    # -- 1. data ----------------------------------------------------------
    print("=" * 74)
    print("DOMAIN CLASSIFIER")
    print("=" * 74)
    train, test, report = prepare(DATA_DIR / "domain_train.csv", label_col="domain")
    print(report.render())
    print(f"  train / test           {len(train)} / {len(test)}")

    labels = sorted({r.label for r in train} | {r.label for r in test})

    # -- 2. encoder -------------------------------------------------------
    embedder = get_embedder()
    print(f"\n  encoder                {embedder.backend} ({embedder.model_name})")
    if embedder.backend == "tfidf":
        # Fit on TRAIN ONLY. Fitting on everything leaks test vocabulary
        # into the representation and inflates the held-out score.
        Embedder.fit_tfidf([r.text for r in train])
        embedder._cache.clear()

    t0 = time.time()
    Xtr, ytr, ltr = build_features(train, embedder)
    Xte, yte, lte = build_features(test, embedder)
    print(f"  embedded               {len(train)+len(test)} texts in {time.time()-t0:.1f}s"
          f"  -> {Xtr.shape[1]}-d")

    # -- 3. train ---------------------------------------------------------
    # C is the only hyperparameter worth tuning here. Small grid, 5-fold,
    # scored on macro-F1 to match the headline metric.
    grid = GridSearchCV(
        LogisticRegression(max_iter=3000, class_weight="balanced"),
        {"C": [0.5, 1.0, 4.0, 16.0, 64.0]},
        cv=StratifiedKFold(5, shuffle=True, random_state=42),
        scoring="f1_macro", n_jobs=-1)
    t0 = time.time()
    grid.fit(Xtr, ytr)
    clf = grid.best_estimator_
    train_s = time.time() - t0
    print(f"  trained                {train_s:.1f}s   best C={grid.best_params_['C']}"
          f"   cv macro-F1={grid.best_score_:.3f}")

    # -- 4. evaluate ------------------------------------------------------
    proba = clf.predict_proba(Xte)
    pred = clf.classes_[proba.argmax(1)]
    conf = proba.max(1)
    f1, per_class = macro_f1(yte, pred, labels)
    acc = float((pred == yte).mean())

    print(f"\n  HELD-OUT macro-F1      {f1:.3f}      accuracy {acc:.3f}   (n={len(yte)})")

    print("\n  per class:")
    for l, s in sorted(zip(labels, per_class), key=lambda x: x[1]):
        bar = "#" * int(s * 30)
        print(f"    {l:<24} {s:.3f}  {bar}")

    # per-language: the evidence for the multilingual claim
    print("\n  per language (the multilingual claim needs this number):")
    lang_scores = {}
    for lang in sorted(set(lte)):
        m = lte == lang
        if m.sum() == 0:
            continue
        lf1, _ = macro_f1(yte[m], pred[m], labels)
        lang_scores[lang] = lf1
        print(f"    {lang:<24} {lf1:.3f}   (n={int(m.sum())})")
    if lang_scores:
        spread = max(lang_scores.values()) - min(lang_scores.values())
        verdict = "OK" if spread < 0.15 else "WARNING - encoder is not aligning the languages"
        print(f"    spread {spread:.3f}  {verdict}")

    # confidence gate: is the 0.55 threshold in the UI actually justified?
    hi, lo = conf >= CONFIDENCE_GATE, conf < CONFIDENCE_GATE
    print(f"\n  confidence gate at {CONFIDENCE_GATE}:")
    if hi.sum():
        print(f"    above  n={int(hi.sum()):3d}  accuracy {float((pred[hi]==yte[hi]).mean()):.3f}"
              f"   <- asserted to the user")
    if lo.sum():
        print(f"    below  n={int(lo.sum()):3d}  accuracy {float((pred[lo]==yte[lo]).mean()):.3f}"
              f"   <- shown as 'needs review'")
    else:
        print(f"    below  n=0   (no test item fell below the gate)")

    # confusion: only the pairs that actually collide
    print("\n  top confusions:")
    conf_pairs = Counter((t, p) for t, p in zip(yte, pred) if t != p)
    if conf_pairs:
        for (t, p), n in conf_pairs.most_common(6):
            print(f"    {t:<22} -> {p:<22} x{n}")
    else:
        print("    none")

    # -- 5. ablation: zero-shot fallback ----------------------------------
    zs_pred, _ = zero_shot_predict(Xte, labels, embedder)
    zs_f1, _ = macro_f1(yte, zs_pred, labels)
    print(f"\n  ABLATION")
    print(f"    zero-shot prototypes   {zs_f1:.3f}   <- fallback when the artifact is missing")
    print(f"    trained LR             {f1:.3f}   ({f1-zs_f1:+.3f})")

    # -- 6. persist -------------------------------------------------------
    joblib.dump({
        "model": clf,
        "labels": list(clf.classes_),
        "encoder": embedder.model_name,
        "backend": embedder.backend,
        "confidence_gate": CONFIDENCE_GATE,
        "version": f"{embedder.backend}+lr-1.0",
    }, MODEL_PATH)

    metrics = {
        "macro_f1": round(f1, 4), "accuracy": round(acc, 4),
        "cv_macro_f1": round(float(grid.best_score_), 4),
        "zero_shot_macro_f1": round(zs_f1, 4),
        "best_C": grid.best_params_["C"],
        "per_class_f1": {l: round(s, 4) for l, s in zip(labels, per_class)},
        "per_language_f1": {k: round(v, 4) for k, v in lang_scores.items()},
        "n_train": len(train), "n_test": len(test),
        "encoder": embedder.model_name, "backend": embedder.backend,
        "train_seconds": round(train_s, 2),
        "data_caveat": (
            "Synthetic LLM-generated corpus. This score measures the model on "
            "data easier and cleaner than reality. Quote it WITH this caveat "
            "and alongside a hand-labelled real-text check."),
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))

    print(f"\n  saved                  {MODEL_PATH.name}  ({MODEL_PATH.stat().st_size/1024:.0f} KB)")
    print(f"  metrics                {METRICS_PATH.name}")
    print(f"  total                  {time.time()-t_start:.1f}s")
    print("\n  SAY THIS OUT LOUD WHEN QUOTING THE NUMBER:")
    print("  synthetic data is cleaner than reality. Report this score together")
    print("  with a hand-labelled real-text check - two honest numbers beat one")
    print("  inflated one, and a judge who probes will find the caveat anyway.")


if __name__ == "__main__":
    main()
