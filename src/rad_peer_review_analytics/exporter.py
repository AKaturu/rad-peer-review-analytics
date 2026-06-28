from __future__ import annotations

import csv
import json
import os

from rad_peer_review_analytics.models import AnalyticsReport, PeerReview


def export_report_csv(report: AnalyticsReport, path: str) -> str:
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    base, _ext = os.path.splitext(path)
    _write_csv(f"{base}_reviewers.csv", _reviewer_rows(report))
    _write_csv(f"{base}_modalities.csv", _modality_rows(report))
    _write_csv(f"{base}_body_parts.csv", _body_part_rows(report))
    _write_csv(f"{base}_trends.csv", _trend_rows(report))
    _write_csv(f"{base}_groups.csv", _group_rows(report))

    return base


def export_report_json(report: AnalyticsReport, path: str) -> str:
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(path, "w") as f:
        json.dump(report.model_dump(), f, indent=2, default=str)
    return path


def export_reviews_csv(reviews: list[PeerReview], path: str) -> str:
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "review_id", "reviewer_id", "reviewee_id", "case_id",
                "score", "score_system", "review_date", "modality",
                "body_part", "finding_type", "is_discrepant", "comment",
            ]
        )
        for r in reviews:
            writer.writerow(
                [
                    r.review_id,
                    r.reviewer_id,
                    r.reviewee_id,
                    r.case_id,
                    r.score,
                    r.score_system,
                    r.review_date.isoformat() if r.review_date else "",
                    r.modality,
                    r.body_part,
                    r.finding_type,
                    "yes" if r.is_discrepant else "no",
                    r.comment,
                ]
            )
    return path


def _write_csv(path: str, rows: list[list[str]]) -> None:
    if not rows:
        return
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)


def _reviewer_rows(report: AnalyticsReport) -> list[list[str]]:
    rows: list[list[str]] = [
        [
            "ReviewerID", "Name", "Subspecialty", "Group",
            "TotalReviews", "AsReviewer", "AsReviewee",
            "AgreementCount", "MinorDiscCount", "MajorDiscCount",
            "AgreementRate", "MajorDiscRate", "AvgScore", "Trend",
        ]
    ]
    for rs in report.reviewer_stats:
        rows.append(
            [
                rs.reviewer_id,
                rs.name,
                rs.subspecialty,
                rs.group_name,
                str(rs.total_reviews),
                str(rs.total_as_reviewer),
                str(rs.total_as_reviewee),
                str(rs.agreement_count),
                str(rs.minor_discrepancy_count),
                str(rs.major_discrepancy_count),
                f"{rs.agreement_rate:.1%}",
                f"{rs.major_discrepancy_rate:.1%}",
                f"{rs.avg_score:.3f}",
                rs.trend_direction,
            ]
        )
    return rows


def _modality_rows(report: AnalyticsReport) -> list[list[str]]:
    rows: list[list[str]] = [
        ["Modality", "TotalReviews", "AgreementRate", "MajorDiscRate", "AvgScore"]
    ]
    for ms in report.modality_stats:
        rows.append(
            [
                ms.modality,
                str(ms.total_reviews),
                f"{ms.agreement_rate:.1%}",
                f"{ms.major_discrepancy_rate:.1%}",
                f"{ms.avg_score:.3f}",
            ]
        )
    return rows


def _body_part_rows(report: AnalyticsReport) -> list[list[str]]:
    rows: list[list[str]] = [
        ["BodyPart", "TotalReviews", "AgreementRate", "MajorDiscRate"]
    ]
    for bs in report.body_part_stats:
        rows.append(
            [
                bs.body_part,
                str(bs.total_reviews),
                f"{bs.agreement_rate:.1%}",
                f"{bs.major_discrepancy_rate:.1%}",
            ]
        )
    return rows


def _trend_rows(report: AnalyticsReport) -> list[list[str]]:
    rows: list[list[str]] = [
        ["YearMonth", "TotalReviews", "AgreementCount", "AgreementRate",
         "MajorDiscCount", "MajorDiscRate"]
    ]
    for mt in report.monthly_trends:
        rows.append(
            [
                mt.year_month,
                str(mt.total_reviews),
                str(mt.agreement_count),
                f"{mt.agreement_rate:.1%}",
                str(mt.major_discrepancy_count),
                f"{mt.major_discrepancy_rate:.1%}",
            ]
        )
    return rows


def _group_rows(report: AnalyticsReport) -> list[list[str]]:
    rows: list[list[str]] = [
        ["Group", "ReviewerCount", "TotalReviews", "AgreementRate",
         "MajorDiscRate", "AvgScore"]
    ]
    for gs in report.group_stats:
        rows.append(
            [
                gs.group_name,
                str(gs.reviewer_count),
                str(gs.total_reviews),
                f"{gs.agreement_rate:.1%}",
                f"{gs.major_discrepancy_rate:.1%}",
                f"{gs.avg_score:.3f}",
            ]
        )
    return rows
