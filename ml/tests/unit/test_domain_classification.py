from app.domain_classification.engine import DOMAIN_PROTOTYPES, _zero_shot_classify, classify_domain
from app.embeddings.engine import embed


def test_trained_classifier_labels_a_clear_water_report_correctly():
    vec = embed("The hand pump in our village has been broken for three weeks and the water is reddish.")
    result = classify_domain(vec)
    assert result.domain == "water"
    assert result.source == "trained"
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.alternatives) == 3


def test_low_confidence_prediction_is_flagged_for_review():
    # Ambiguous, generic text should not be asserted with high confidence.
    vec = embed("There is a problem.")
    result = classify_domain(vec)
    if result.confidence < 0.55:
        assert result.needs_review is True


def test_zero_shot_fallback_never_errors_and_covers_all_prototypes():
    import numpy as np

    vec = embed("Farmers are struggling because the crop failed due to lack of irrigation")
    result = _zero_shot_classify(np.asarray(vec, dtype="float32"))
    assert result.source == "zero_shot_fallback"
    assert result.needs_review is True
    assert result.domain in DOMAIN_PROTOTYPES


def test_classification_never_returns_a_merge_or_decision_field():
    vec = embed("Streetlight broken near the market")
    result = classify_domain(vec)
    assert not hasattr(result, "decision")
    assert not hasattr(result, "action")
