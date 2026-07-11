from rad_peer_review_analytics.models import PeerReview
from rad_peer_review_analytics.scoring import (
    classify_review,
    get_score_label,
    get_score_weight,
    is_discrepant,
    is_major_discrepant,
    radpeer_to_standard,
    standard_to_radpeer,
)


class TestGetScoreWeight:
    def test_radpeer_agree(self):
        assert get_score_weight("1", "radpeer") == 1.0

    def test_radpeer_minor(self):
        assert get_score_weight("2", "radpeer") == 0.75

    def test_radpeer_disagree_not_perceived(self):
        assert get_score_weight("3a", "radpeer") == 0.25

    def test_radpeer_disagree_should_perceive(self):
        assert get_score_weight("3b", "radpeer") == 0.0

    def test_standard_agree(self):
        assert get_score_weight("agree", "standard") == 1.0

    def test_standard_minor(self):
        assert get_score_weight("minor_discrepancy", "standard") == 0.5

    def test_standard_major(self):
        assert get_score_weight("major_discrepancy", "standard") == 0.0

    def test_standard_not_actionable(self):
        assert get_score_weight("not_actionable_discrepancy", "standard") == 0.5

    def test_unknown_score_default(self):
        assert get_score_weight("unknown", "radpeer") == 0.5

    def test_score_from_other_system_is_not_reused(self):
        assert get_score_weight("agree", "radpeer") == 0.5
        assert get_score_weight("1", "standard") == 0.5


class TestGetScoreLabel:
    def test_radpeer_1(self):
        assert get_score_label("1", "radpeer") == "Agree"

    def test_radpeer_3b(self):
        assert "should be perceived" in get_score_label("3b", "radpeer")

    def test_standard_agree(self):
        assert get_score_label("agree", "standard") == "Agree"

    def test_unknown(self):
        assert get_score_label("??", "radpeer") == "Unknown"


class TestIsDiscrepant:
    def test_radpeer_agree_not_discrepant(self):
        assert is_discrepant("1", "radpeer") is False

    def test_radpeer_minor_not_discrepant(self):
        assert is_discrepant("2", "radpeer") is False

    def test_radpeer_3a_discrepant(self):
        assert is_discrepant("3a", "radpeer") is True

    def test_radpeer_3b_discrepant(self):
        assert is_discrepant("3b", "radpeer") is True

    def test_standard_agree_not_discrepant(self):
        assert is_discrepant("agree", "standard") is False

    def test_standard_minor_discrepant(self):
        assert is_discrepant("minor_discrepancy", "standard") is True

    def test_standard_major_discrepant(self):
        assert is_discrepant("major_discrepancy", "standard") is True


class TestIsMajorDiscrepant:
    def test_radpeer_1_not_major(self):
        assert is_major_discrepant("1", "radpeer") is False

    def test_radpeer_3b_major(self):
        assert is_major_discrepant("3b", "radpeer") is True

    def test_radpeer_3a_not_major(self):
        assert is_major_discrepant("3a", "radpeer") is False

    def test_standard_major(self):
        assert is_major_discrepant("major_discrepancy", "standard") is True

    def test_standard_minor_not_major(self):
        assert is_major_discrepant("minor_discrepancy", "standard") is False


class TestClassifyReview:
    def test_marks_discrepant(self):
        review = PeerReview(
            review_id="R1",
            reviewer_id="R001",
            reviewee_id="R002",
            case_id="C001",
            score="3b",
        )
        result = classify_review(review)
        assert result.is_discrepant is True
        assert result is review

    def test_marks_not_discrepant(self):
        review = PeerReview(
            review_id="R1",
            reviewer_id="R001",
            reviewee_id="R002",
            case_id="C001",
            score="1",
        )
        result = classify_review(review)
        assert result.is_discrepant is False
        assert result is review


class TestRadpeerToStandard:
    def test_1_to_agree(self):
        assert radpeer_to_standard("1") == "agree"

    def test_2_remains_agreement(self):
        assert radpeer_to_standard("2") == "agree"

    def test_3a_to_not_actionable(self):
        assert radpeer_to_standard("3a") == "not_actionable_discrepancy"

    def test_3b_to_major(self):
        assert radpeer_to_standard("3b") == "major_discrepancy"

    def test_unknown_defaults_to_agree(self):
        assert radpeer_to_standard("?") == "agree"


class TestStandardToRadpeer:
    def test_agree_to_1(self):
        assert standard_to_radpeer("agree") == "1"

    def test_minor_to_3a(self):
        assert standard_to_radpeer("minor_discrepancy") == "3a"

    def test_major_to_3b(self):
        assert standard_to_radpeer("major_discrepancy") == "3b"

    def test_not_actionable_to_3a(self):
        assert standard_to_radpeer("not_actionable_discrepancy") == "3a"

    def test_unknown_defaults_to_1(self):
        assert standard_to_radpeer("?") == "1"
