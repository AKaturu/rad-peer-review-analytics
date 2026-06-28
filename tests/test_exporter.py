import json
import os
import tempfile

from rad_peer_review_analytics.exporter import (
    export_report_csv,
    export_report_json,
    export_reviews_csv,
)
from rad_peer_review_analytics.models import (
    AnalyticsReport,
    BodyPartStats,
    GroupStats,
    ModalityStats,
    MonthlyTrend,
    PeerReview,
    ReviewerStats,
)


def _sample_report() -> AnalyticsReport:
    return AnalyticsReport(
        total_reviews=10,
        total_reviewers=3,
        date_range="2024-01-01 to 2024-12-31",
        overall_agreement_rate=0.8,
        overall_major_discrepancy_rate=0.1,
        overall_avg_score=0.85,
        reviewer_stats=[
            ReviewerStats(
                reviewer_id="R001",
                name="Dr. A",
                group_name="Group X",
                total_reviews=5,
                total_as_reviewer=3,
                total_as_reviewee=2,
                agreement_count=4,
                minor_discrepancy_count=1,
                major_discrepancy_count=0,
                agreement_rate=0.8,
                major_discrepancy_rate=0.0,
                avg_score=0.85,
                trend_direction="stable",
            ),
            ReviewerStats(
                reviewer_id="R002",
                name="Dr. B",
                group_name="Group Y",
                total_reviews=5,
                total_as_reviewer=2,
                total_as_reviewee=3,
                agreement_count=3,
                minor_discrepancy_count=0,
                major_discrepancy_count=2,
                agreement_rate=0.6,
                major_discrepancy_rate=0.4,
                avg_score=0.65,
                trend_direction="declining",
            ),
        ],
        group_stats=[
            GroupStats(
                group_name="Group X", reviewer_count=2, total_reviews=8,
                agreement_rate=0.75, major_discrepancy_rate=0.125, avg_score=0.82,
            ),
        ],
        modality_stats=[
            ModalityStats(
                modality="CT", total_reviews=6, agreement_rate=0.833,
                major_discrepancy_rate=0.167, avg_score=0.83,
            ),
            ModalityStats(
                modality="MRI", total_reviews=4, agreement_rate=0.75,
                major_discrepancy_rate=0.0, avg_score=0.88,
            ),
        ],
        body_part_stats=[
            BodyPartStats(
                body_part="CHEST", total_reviews=7, agreement_rate=0.857,
                major_discrepancy_rate=0.143,
            ),
            BodyPartStats(
                body_part="BRAIN", total_reviews=3, agreement_rate=0.667,
                major_discrepancy_rate=0.0,
            ),
        ],
        monthly_trends=[
            MonthlyTrend(
                year_month="2024-01", total_reviews=3, agreement_count=2,
                agreement_rate=0.667, major_discrepancy_count=1,
                major_discrepancy_rate=0.333,
            ),
            MonthlyTrend(
                year_month="2024-02", total_reviews=7, agreement_count=6,
                agreement_rate=0.857, major_discrepancy_count=0,
                major_discrepancy_rate=0.0,
            ),
        ],
        top_discrepant_modalities=["CT", "MRI"],
    )


def _sample_reviews() -> list[PeerReview]:
    return [
        PeerReview(
            review_id="R1", reviewer_id="R001", reviewee_id="R002",
            case_id="C001", score="1",
        ),
        PeerReview(
            review_id="R2", reviewer_id="R001", reviewee_id="R003",
            case_id="C002", score="3b", is_discrepant=True,
        ),
    ]


class TestExportReviewsCSV:
    def test_exports_file(self):
        reviews = _sample_reviews()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "reviews.csv")
            result = export_reviews_csv(reviews, path)
            assert result == path
            assert os.path.exists(path)
            with open(path) as f:
                content = f.read()
            assert "review_id" in content
            assert "R1" in content
            assert "R2" in content
            assert "yes" in content

    def test_creates_directories(self):
        reviews = _sample_reviews()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sub", "reviews.csv")
            result = export_reviews_csv(reviews, path)
            assert result == path
            assert os.path.exists(path)


class TestExportReportCSV:
    def test_exports_multiple_files(self):
        report = _sample_report()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "report.csv")
            base = export_report_csv(report, path)
            assert base == os.path.join(tmp, "report")
            assert os.path.exists(f"{base}_reviewers.csv")
            assert os.path.exists(f"{base}_modalities.csv")
            assert os.path.exists(f"{base}_body_parts.csv")
            assert os.path.exists(f"{base}_trends.csv")
            assert os.path.exists(f"{base}_groups.csv")

    def test_csv_content(self):
        report = _sample_report()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "r.csv")
            export_report_csv(report, path)
            with open(os.path.join(tmp, "r_reviewers.csv")) as f:
                content = f.read()
            assert "Dr. A" in content
            assert "Dr. B" in content
            with open(os.path.join(tmp, "r_modalities.csv")) as f:
                content = f.read()
            assert "CT" in content
            assert "MRI" in content
            with open(os.path.join(tmp, "r_body_parts.csv")) as f:
                content = f.read()
            assert "CHEST" in content
            with open(os.path.join(tmp, "r_trends.csv")) as f:
                content = f.read()
            assert "2024-01" in content
            with open(os.path.join(tmp, "r_groups.csv")) as f:
                content = f.read()
            assert "Group X" in content

    def test_empty_report(self):
        report = AnalyticsReport()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "empty.csv")
            export_report_csv(report, path)
            # Header-only CSV files are written even with no data
            rpath = os.path.join(tmp, "empty_reviewers.csv")
            assert os.path.exists(rpath)
            with open(rpath) as f:
                assert "ReviewerID" in f.read()

    def test_creates_directories(self):
        report = _sample_report()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "deep", "nested", "report.csv")
            export_report_csv(report, path)
            assert os.path.exists(os.path.join(tmp, "deep", "nested", "report_reviewers.csv"))


class TestExportReportJSON:
    def test_exports_file(self):
        report = _sample_report()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "report.json")
            result = export_report_json(report, path)
            assert result == path
            assert os.path.exists(path)
            with open(path) as f:
                data = json.load(f)
            assert data["total_reviews"] == 10
            assert data["overall_agreement_rate"] == 0.8
            assert len(data["reviewer_stats"]) == 2

    def test_creates_directories(self):
        report = _sample_report()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "deep", "report.json")
            export_report_json(report, path)
            assert os.path.exists(path)
