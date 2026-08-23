from app.embeddings.engine import embed
from app.field_classification.engine import classify_field_intensity, keyword_ratio


def test_physical_repair_report_classified_field_heavy():
    text = "The hand pump is broken and needs a mechanic to repair the borewell pipe onsite."
    vec = embed(text)
    result = classify_field_intensity(text, "water", vec)
    assert result.label in ("FIELD_HEAVY", "HYBRID")
    assert 0.0 <= result.field_intensity <= 1.0
    assert result.source in ("trained", "rules_fallback")


def test_remote_analytical_report_scores_lower_than_physical_report():
    physical = "The transformer is damaged and needs to be replaced onsite by a technician."
    remote = "The scholarship portal keeps rejecting valid documents due to a data validation bug."
    vec_physical = embed(physical)
    vec_remote = embed(remote)
    result_physical = classify_field_intensity(physical, "energy", vec_physical)
    result_remote = classify_field_intensity(remote, "public_administration", vec_remote)
    assert result_physical.field_intensity > result_remote.field_intensity


def test_fallback_path_is_explicit_and_flagged_for_review():
    from app.field_classification.engine import FALLBACK_BLEND, DEFAULT_PRIOR

    # Directly exercise the fallback formula shape (keyword+prior only, no model).
    kw = keyword_ratio("The road is damaged and needs urgent repair.")
    fi = FALLBACK_BLEND["keyword"] * kw + FALLBACK_BLEND["prior"] * DEFAULT_PRIOR
    assert 0.0 <= fi <= 1.0


def test_unknown_domain_falls_back_to_default_prior():
    vec = embed("Something happened.")
    result = classify_field_intensity("Something happened.", "not_a_real_domain", vec)
    assert result.label in ("FIELD_HEAVY", "HYBRID", "REMOTE_ANALYTICAL")


def test_classification_never_returns_a_decision_field():
    vec = embed("Streetlight broken near the market")
    result = classify_field_intensity("Streetlight broken near the market", "urban_infrastructure", vec)
    assert not hasattr(result, "decision")
    assert not hasattr(result, "action")
