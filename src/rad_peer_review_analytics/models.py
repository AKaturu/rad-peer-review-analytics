from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class ScoreValue(StrEnum):
    agree = "agree"
    minor = "minor_discrepancy"
    major = "major_discrepancy"
    not_actionable = "not_actionable_discrepancy"


class ScoreLabel(StrEnum):
    agree = "Agree"
    minor = "Minor Discrepancy (not clinically significant)"
    major = "Major Discrepancy (clinically significant)"
    not_actionable = "Not Actionable Discrepancy"


class RadpeerView(StrEnum):
    one = "1"
    two = "2"
    three_a = "3a"
    three_b = "3b"


SCORE_WEIGHTS: dict[str, float] = {
    "1": 1.0,
    "2": 0.75,
    "3a": 0.25,
    "3b": 0.0,
    "agree": 1.0,
    "minor_discrepancy": 0.5,
    "major_discrepancy": 0.0,
    "not_actionable_discrepancy": 0.5,
}

SCORE_LABELS: dict[str, str] = {
    "1": "Agree",
    "2": "Agree with minor disagreement",
    "3a": "Disagree - not normally perceived",
    "3b": "Disagree - should be perceived",
    "agree": "Agree",
    "minor_discrepancy": "Minor Discrepancy (not clinically significant)",
    "major_discrepancy": "Major Discrepancy (clinically significant)",
    "not_actionable_discrepancy": "Discrepancy - not actionable",
}


class Reviewer(BaseModel):
    reviewer_id: str
    name: str = ""
    subspecialty: str = ""
    group_name: str = ""


class ReviewCase(BaseModel):
    case_id: str
    modality: str = ""
    body_part: str = ""
    study_date: date | None = None
    description: str = ""


class PeerReview(BaseModel):
    review_id: str
    reviewer_id: str
    reviewee_id: str
    case_id: str
    score: str
    score_system: str = "radpeer"
    review_date: date | None = None
    modality: str = ""
    body_part: str = ""
    finding_type: str = ""
    comment: str = ""
    is_discrepant: bool = False


class ReviewImport(BaseModel):
    rows: list[PeerReview]
    skipped: int = 0
    errors: list[str] = Field(default_factory=list)


class ReviewerStats(BaseModel):
    reviewer_id: str
    name: str = ""
    subspecialty: str = ""
    group_name: str = ""
    total_reviews: int = 0
    total_as_reviewer: int = 0
    total_as_reviewee: int = 0
    agreement_count: int = 0
    minor_discrepancy_count: int = 0
    major_discrepancy_count: int = 0
    agreement_rate: float = 0.0
    major_discrepancy_rate: float = 0.0
    avg_score: float = 0.0
    trend_direction: str = "stable"


class GroupStats(BaseModel):
    group_name: str = ""
    reviewer_count: int = 0
    total_reviews: int = 0
    agreement_rate: float = 0.0
    major_discrepancy_rate: float = 0.0
    avg_score: float = 0.0


class ModalityStats(BaseModel):
    modality: str
    total_reviews: int = 0
    agreement_rate: float = 0.0
    major_discrepancy_rate: float = 0.0
    avg_score: float = 0.0


class BodyPartStats(BaseModel):
    body_part: str
    total_reviews: int = 0
    agreement_rate: float = 0.0
    major_discrepancy_rate: float = 0.0


class MonthlyTrend(BaseModel):
    year_month: str
    total_reviews: int = 0
    agreement_count: int = 0
    agreement_rate: float = 0.0
    major_discrepancy_count: int = 0
    major_discrepancy_rate: float = 0.0


class AnalyticsReport(BaseModel):
    total_reviews: int = 0
    total_reviewers: int = 0
    date_range: str = ""
    overall_agreement_rate: float = 0.0
    overall_major_discrepancy_rate: float = 0.0
    overall_avg_score: float = 0.0
    reviewer_stats: list[ReviewerStats] = Field(default_factory=list)
    group_stats: list[GroupStats] = Field(default_factory=list)
    modality_stats: list[ModalityStats] = Field(default_factory=list)
    body_part_stats: list[BodyPartStats] = Field(default_factory=list)
    monthly_trends: list[MonthlyTrend] = Field(default_factory=list)
    top_discrepant_modalities: list[str] = Field(default_factory=list)
