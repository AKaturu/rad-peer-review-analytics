from datetime import date

from rad_peer_review_analytics.models import (
    SCORE_LABELS,
    SCORE_WEIGHTS,
    AnalyticsReport,
    BodyPartStats,
    GroupStats,
    ModalityStats,
    MonthlyTrend,
    PeerReview,
    RadpeerView,
    ReviewCase,
    Reviewer,
    ReviewerStats,
    ReviewImport,
    ScoreLabel,
    ScoreValue,
)


class TestEnums:
    def test_score_value_members(self):
        assert ScoreValue.agree == "agree"
        assert ScoreValue.minor == "minor_discrepancy"
        assert ScoreValue.major == "major_discrepancy"
        assert ScoreValue.not_actionable == "not_actionable_discrepancy"

    def test_score_label_members(self):
        assert ScoreLabel.agree == "Agree"
        assert "Minor Discrepancy" in ScoreLabel.minor
        assert "Major Discrepancy" in ScoreLabel.major

    def test_radpeer_view_members(self):
        assert RadpeerView.one == "1"
        assert RadpeerView.two == "2"
        assert RadpeerView.three_a == "3a"
        assert RadpeerView.three_b == "3b"


class TestConstants:
    def test_score_weights_radpeer(self):
        assert SCORE_WEIGHTS["1"] == 1.0
        assert SCORE_WEIGHTS["2"] == 0.75
        assert SCORE_WEIGHTS["3a"] == 0.25
        assert SCORE_WEIGHTS["3b"] == 0.0

    def test_score_weights_standard(self):
        assert SCORE_WEIGHTS["agree"] == 1.0
        assert SCORE_WEIGHTS["minor_discrepancy"] == 0.5
        assert SCORE_WEIGHTS["major_discrepancy"] == 0.0
        assert SCORE_WEIGHTS["not_actionable_discrepancy"] == 0.5

    def test_score_labels_radpeer(self):
        assert SCORE_LABELS["1"] == "Agree"
        assert SCORE_LABELS["3b"] == "Disagree - should be perceived"


class TestReviewer:
    def test_minimal(self):
        r = Reviewer(reviewer_id="R001")
        assert r.reviewer_id == "R001"
        assert r.name == ""
        assert r.subspecialty == ""
        assert r.group_name == ""

    def test_full(self):
        r = Reviewer(
            reviewer_id="R001", name="Dr. Smith",
            subspecialty="body", group_name="Group A",
        )
        assert r.name == "Dr. Smith"
        assert r.subspecialty == "body"
        assert r.group_name == "Group A"


class TestReviewCase:
    def test_minimal(self):
        c = ReviewCase(case_id="C001")
        assert c.case_id == "C001"
        assert c.modality == ""

    def test_with_date(self):
        c = ReviewCase(case_id="C001", modality="CT", study_date=date(2024, 6, 1))
        assert c.study_date == date(2024, 6, 1)


class TestPeerReview:
    def test_defaults(self):
        pr = PeerReview(
            review_id="R1", reviewer_id="R001", reviewee_id="R002",
            case_id="C001", score="1",
        )
        assert pr.score_system == "radpeer"
        assert pr.review_date is None
        assert pr.is_discrepant is False

    def test_standard_system(self):
        pr = PeerReview(
            review_id="R1", reviewer_id="R001", reviewee_id="R002",
            case_id="C001", score="agree", score_system="standard",
        )
        assert pr.score_system == "standard"

    def test_with_all_fields(self):
        pr = PeerReview(
            review_id="R1", reviewer_id="R001", reviewee_id="R002",
            case_id="C001", score="3b", score_system="radpeer",
            review_date=date(2024, 5, 10), modality="CT", body_part="CHEST",
            finding_type="nodule", comment="Missed finding",
        )
        assert pr.review_date == date(2024, 5, 10)
        assert pr.modality == "CT"
        assert pr.body_part == "CHEST"


class TestReviewImport:
    def test_defaults(self):
        ri = ReviewImport(rows=[])
        assert ri.skipped == 0
        assert ri.errors == []

    def test_with_data(self):
        pr = PeerReview(
            review_id="R1", reviewer_id="R001", reviewee_id="R002",
            case_id="C001", score="1",
        )
        ri = ReviewImport(rows=[pr], skipped=1, errors=["error 1"])
        assert len(ri.rows) == 1
        assert ri.skipped == 1
        assert ri.errors == ["error 1"]


class TestReviewerStats:
    def test_defaults(self):
        rs = ReviewerStats(reviewer_id="R001")
        assert rs.total_reviews == 0
        assert rs.agreement_rate == 0.0
        assert rs.trend_direction == "stable"


class TestGroupStats:
    def test_defaults(self):
        gs = GroupStats()
        assert gs.group_name == ""
        assert gs.reviewer_count == 0


class TestModalityStats:
    def test_minimal(self):
        ms = ModalityStats(modality="CT")
        assert ms.total_reviews == 0


class TestBodyPartStats:
    def test_minimal(self):
        bs = BodyPartStats(body_part="CHEST")
        assert bs.total_reviews == 0


class TestMonthlyTrend:
    def test_minimal(self):
        mt = MonthlyTrend(year_month="2024-01")
        assert mt.total_reviews == 0


class TestAnalyticsReport:
    def test_defaults(self):
        ar = AnalyticsReport()
        assert ar.total_reviews == 0
        assert ar.reviewer_stats == []
        assert ar.group_stats == []
        assert ar.modality_stats == []
        assert ar.body_part_stats == []
        assert ar.monthly_trends == []
        assert ar.top_discrepant_modalities == []
