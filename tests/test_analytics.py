from datetime import date

from rad_peer_review_analytics.analytics import AnalyticsEngine
from rad_peer_review_analytics.models import PeerReview, Reviewer


def _make_review(
    review_id: str,
    reviewer_id: str,
    reviewee_id: str,
    score: str,
    score_system: str = "radpeer",
    review_date: date | None = None,
    modality: str = "",
    body_part: str = "",
) -> PeerReview:
    return PeerReview(
        review_id=review_id,
        reviewer_id=reviewer_id,
        reviewee_id=reviewee_id,
        case_id=f"CASE{review_id}",
        score=score,
        score_system=score_system,
        review_date=review_date,
        modality=modality,
        body_part=body_part,
    )


AGREE = _make_review("R1", "R001", "R002", "1")
AGREE2 = _make_review("R2", "R002", "R001", "1")
MINOR = _make_review("R3", "R001", "R002", "2")
DISC_3A = _make_review("R4", "R001", "R002", "3a")
DISC_3B = _make_review("R5", "R001", "R002", "3b")

REVIEWER_A = Reviewer(reviewer_id="R001", name="Dr. A", group_name="Group X")
REVIEWER_B = Reviewer(reviewer_id="R002", name="Dr. B", group_name="Group X")
REVIEWER_C = Reviewer(reviewer_id="R003", name="Dr. C", group_name="Group Y")

REVIEW_WITH_DATES = [
    _make_review("D1", "R001", "R002", "1", review_date=date(2024, 1, 15),
                 modality="CT", body_part="CHEST"),
    _make_review("D2", "R001", "R002", "1", review_date=date(2024, 2, 10),
                 modality="CT", body_part="CHEST"),
    _make_review("D3", "R001", "R002", "1", review_date=date(2024, 3, 5),
                 modality="XR", body_part="CHEST"),
    _make_review("D4", "R001", "R002", "3b", review_date=date(2024, 4, 20),
                 modality="MRI", body_part="BRAIN"),
    _make_review("D5", "R002", "R001", "1", review_date=date(2024, 5, 1),
                 modality="CT", body_part="ABDOMEN"),
]


class TestAnalyticsEngine:
    def test_empty_engine(self):
        engine = AnalyticsEngine()
        report = engine.generate_report()
        assert report.total_reviews == 0
        assert report.total_reviewers == 0
        assert report.overall_agreement_rate == 0.0

    def test_load_and_report_basic(self):
        engine = AnalyticsEngine()
        engine.load([AGREE, DISC_3B])
        report = engine.generate_report()
        assert report.total_reviews == 2
        assert report.overall_agreement_rate == 0.5
        assert report.overall_major_discrepancy_rate == 0.5
        assert report.overall_avg_score == 0.5  # (1.0 + 0.0) / 2

    def test_all_agreements(self):
        engine = AnalyticsEngine()
        engine.load([AGREE, AGREE2])
        report = engine.generate_report()
        assert report.overall_agreement_rate == 1.0
        assert report.overall_major_discrepancy_rate == 0.0

    def test_all_major_discrepancies(self):
        engine = AnalyticsEngine()
        engine.load([DISC_3B, DISC_3B])
        report = engine.generate_report()
        assert report.overall_agreement_rate == 0.0
        assert report.overall_major_discrepancy_rate == 1.0

    def test_minor_not_major_discrepancy(self):
        engine = AnalyticsEngine()
        engine.load([MINOR])
        report = engine.generate_report()
        assert report.overall_major_discrepancy_rate == 0.0

    def test_reviewer_stats_count(self):
        engine = AnalyticsEngine()
        engine.load([AGREE, DISC_3B], [REVIEWER_A, REVIEWER_B])
        report = engine.generate_report()
        assert len(report.reviewer_stats) == 2

    def test_reviewer_agreement_rate(self):
        # R001 appears in AGREE (reviewer) and DISC_3B (reviewer) and AGREE2 (reviewee) = 3 total
        engine = AnalyticsEngine()
        engine.load([AGREE, AGREE2, DISC_3B], [REVIEWER_A])
        report = engine.generate_report()
        r1_stats = next(rs for rs in report.reviewer_stats if rs.reviewer_id == "R001")
        assert r1_stats.total_reviews == 3
        assert r1_stats.total_as_reviewer == 2
        assert r1_stats.agreement_count == 1  # only AGREE count as agreement for R001

    def test_reviewer_trend_stable_few_reviews(self):
        engine = AnalyticsEngine()
        engine.load([AGREE, DISC_3B], [REVIEWER_A])
        report = engine.generate_report()
        r1_stats = next(rs for rs in report.reviewer_stats if rs.reviewer_id == "R001")
        assert r1_stats.trend_direction == "stable"

    def test_reviewer_trend_improving(self):
        reviews = [
            _make_review(f"T{i}", "R001", "R002", "3b", review_date=date(2024, 1, i))
            for i in range(1, 5)
        ] + [
            _make_review(f"T{i+10}", "R001", "R002", "1", review_date=date(2024, 2, i))
            for i in range(1, 5)
        ]
        engine = AnalyticsEngine()
        engine.load(reviews, [REVIEWER_A])
        report = engine.generate_report()
        r1_stats = next(rs for rs in report.reviewer_stats if rs.reviewer_id == "R001")
        assert r1_stats.trend_direction == "improving"

    def test_reviewer_trend_declining(self):
        reviews = [
            _make_review(f"T{i}", "R001", "R002", "1", review_date=date(2024, 1, i))
            for i in range(1, 5)
        ] + [
            _make_review(f"T{i+10}", "R001", "R002", "3b", review_date=date(2024, 2, i))
            for i in range(1, 5)
        ]
        engine = AnalyticsEngine()
        engine.load(reviews, [REVIEWER_A])
        report = engine.generate_report()
        r1_stats = next(rs for rs in report.reviewer_stats if rs.reviewer_id == "R001")
        assert r1_stats.trend_direction == "declining"

    def test_group_stats(self):
        engine = AnalyticsEngine()
        engine.load([AGREE, DISC_3B], [REVIEWER_A, REVIEWER_B])
        report = engine.generate_report()
        assert len(report.group_stats) > 0
        gx = next(gs for gs in report.group_stats if gs.group_name == "Group X")
        assert gx.total_reviews == 2

    def test_modality_stats(self):
        reviews = [
            _make_review("M1", "R001", "R002", "1", modality="CT"),
            _make_review("M2", "R001", "R002", "3b", modality="CT"),
            _make_review("M3", "R001", "R002", "1", modality="MRI"),
        ]
        engine = AnalyticsEngine()
        engine.load(reviews)
        report = engine.generate_report()
        ct_stats = next(ms for ms in report.modality_stats if ms.modality == "CT")
        assert ct_stats.total_reviews == 2
        assert ct_stats.agreement_rate == 0.5
        mri_stats = next(ms for ms in report.modality_stats if ms.modality == "MRI")
        assert mri_stats.total_reviews == 1
        assert mri_stats.agreement_rate == 1.0

    def test_body_part_stats(self):
        reviews = [
            _make_review("B1", "R001", "R002", "1", body_part="CHEST"),
            _make_review("B2", "R001", "R002", "3b", body_part="CHEST"),
            _make_review("B3", "R001", "R002", "1", body_part="BRAIN"),
        ]
        engine = AnalyticsEngine()
        engine.load(reviews)
        report = engine.generate_report()
        chest_stats = next(bs for bs in report.body_part_stats if bs.body_part == "CHEST")
        assert chest_stats.total_reviews == 2
        assert chest_stats.agreement_rate == 0.5

    def test_monthly_trends(self):
        engine = AnalyticsEngine()
        engine.load(REVIEW_WITH_DATES)
        report = engine.generate_report()
        assert len(report.monthly_trends) > 0
        jan = next(mt for mt in report.monthly_trends if mt.year_month == "2024-01")
        assert jan.total_reviews == 1
        assert jan.agreement_rate == 1.0
        apr = next(mt for mt in report.monthly_trends if mt.year_month == "2024-04")
        assert apr.agreement_rate == 0.0

    def test_date_range(self):
        engine = AnalyticsEngine()
        engine.load(REVIEW_WITH_DATES)
        report = engine.generate_report()
        assert "2024-01-15" in report.date_range
        assert "2024-05-01" in report.date_range

    def test_top_discrepant_modalities(self):
        reviews = [
            _make_review("X1", "R001", "R002", "3a", modality="CT"),
            _make_review("X2", "R001", "R002", "3b", modality="CT"),
            _make_review("X3", "R001", "R002", "1", modality="MRI"),
            _make_review("X4", "R001", "R002", "3a", modality="XR"),
        ]
        engine = AnalyticsEngine()
        engine.load(reviews)
        report = engine.generate_report()
        assert "CT" in report.top_discrepant_modalities

    def test_standard_system_scores(self):
        std_agree = _make_review("S1", "R001", "R002", "agree", score_system="standard")
        std_major = _make_review("S2", "R001", "R002", "major_discrepancy", score_system="standard")
        engine = AnalyticsEngine()
        engine.load([std_agree, std_major])
        report = engine.generate_report()
        assert report.overall_agreement_rate == 0.5
        assert report.overall_major_discrepancy_rate == 0.5

    def test_count_unique_reviewers_without_reviewers_dict(self):
        reviews = [
            _make_review("U1", "R001", "R002", "1"),
            _make_review("U2", "R003", "R004", "1"),
        ]
        engine = AnalyticsEngine()
        engine.load(reviews)
        report = engine.generate_report()
        assert report.total_reviewers == 4

    def test_standard_minor_is_not_major(self):
        std_minor = _make_review("N1", "R001", "R002", "minor_discrepancy", score_system="standard")
        engine = AnalyticsEngine()
        engine.load([std_minor])
        report = engine.generate_report()
        assert report.overall_major_discrepancy_rate == 0.0
        assert report.overall_agreement_rate == 0.0
