from __future__ import annotations

from rad_peer_review_analytics.models import SCORE_WEIGHTS, PeerReview


def get_score_weight(score: str, score_system: str = "radpeer") -> float:
    if score_system == "radpeer":
        return SCORE_WEIGHTS.get(score, 0.5)
    return SCORE_WEIGHTS.get(score, 0.5)


def get_score_label(score: str, score_system: str = "radpeer") -> str:
    if score_system == "radpeer":
        labels = {
            "1": "Agree",
            "2": "Agree with minor disagreement",
            "3a": "Disagree - not normally perceived",
            "3b": "Disagree - should be perceived",
        }
        return labels.get(score, "Unknown")
    labels = {
        "agree": "Agree",
        "minor_discrepancy": "Minor Discrepancy",
        "major_discrepancy": "Major Discrepancy",
        "not_actionable_discrepancy": "Not Actionable Discrepancy",
    }
    return labels.get(score, "Unknown")


def is_discrepant(score: str, score_system: str = "radpeer") -> bool:
    if score_system == "radpeer":
        return score in ("3a", "3b")
    return score in ("minor_discrepancy", "major_discrepancy", "not_actionable_discrepancy")


def is_major_discrepant(score: str, score_system: str = "radpeer") -> bool:
    if score_system == "radpeer":
        return score == "3b"
    return score == "major_discrepancy"


def classify_review(review: PeerReview) -> PeerReview:
    review.is_discrepant = is_discrepant(review.score, review.score_system)
    return review


def radpeer_to_standard(radpeer_score: str) -> str:
    mapping = {
        "1": "agree",
        "2": "minor_discrepancy",
        "3a": "major_discrepancy",
        "3b": "major_discrepancy",
    }
    return mapping.get(radpeer_score, "agree")


def standard_to_radpeer(standard_score: str) -> str:
    mapping = {
        "agree": "1",
        "minor_discrepancy": "2",
        "major_discrepancy": "3b",
        "not_actionable_discrepancy": "3a",
    }
    return mapping.get(standard_score, "1")
