from __future__ import annotations

import csv
import io
from datetime import date, datetime

from rad_peer_review_analytics.models import PeerReview, ReviewImport


def import_csv(text: str) -> ReviewImport:
    result = ReviewImport(rows=[])
    reader = csv.DictReader(io.StringIO(text))

    for row in reader:
        try:
            review = _row_to_review(row)
            result.rows.append(review)
        except Exception as e:
            result.errors.append(f"Row {reader.line_num}: {e}")
            result.skipped += 1

    return result


def import_csv_file(path: str) -> ReviewImport:
    with open(path, newline="", encoding="utf-8") as f:
        return import_csv(f.read())


def _row_to_review(row: dict[str, str]) -> PeerReview:
    review_id = row.get("review_id") or row.get("ReviewID") or ""
    reviewer_id = row.get("reviewer_id") or row.get("ReviewerID") or row.get("ReviewerId") or ""
    reviewee_id = row.get("reviewee_id") or row.get("RevieweeID") or row.get("RevieweeId") or ""
    case_id = row.get("case_id") or row.get("CaseID") or ""
    score = row.get("score") or row.get("Score") or ""
    score_system = row.get("score_system") or row.get("ScoreSystem") or "radpeer"

    if not reviewer_id or not score:
        raise ValueError("Missing required fields: reviewer_id and score")

    review_date: date | None = None
    rd = row.get("review_date") or row.get("ReviewDate") or ""
    if rd:
        try:
            review_date = datetime.strptime(rd.strip(), "%Y-%m-%d").date()
        except ValueError:
            try:
                review_date = datetime.strptime(rd.strip(), "%m/%d/%Y").date()
            except ValueError:
                pass

    return PeerReview(
        review_id=review_id,
        reviewer_id=reviewer_id,
        reviewee_id=reviewee_id,
        case_id=case_id,
        score=score,
        score_system=score_system,
        review_date=review_date,
        modality=row.get("modality") or row.get("Modality") or "",
        body_part=row.get("body_part") or row.get("BodyPart") or "",
        finding_type=row.get("finding_type") or row.get("FindingType") or "",
        comment=row.get("comment") or row.get("Comment") or "",
    )
