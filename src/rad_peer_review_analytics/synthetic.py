from __future__ import annotations

import random
from datetime import date, timedelta

from rad_peer_review_analytics.models import PeerReview, Reviewer

_RADPEER_SCORES = ["1", "2", "3a", "3b"]
_STANDARD_SCORES = ["agree", "minor_discrepancy", "major_discrepancy"]
_MODALITIES = ["CT", "MRI", "XR", "US", "MAMMO", "PET", "NM"]
_BODY_PARTS = ["CHEST", "BRAIN", "ABDOMEN", "PELVIS", "SPINE", "BREAST", "EXTREMITY", "HEAD/NECK"]
_FINDING_TYPES = [
    "mass",
    "nodule",
    "fracture",
    "infection",
    "hemorrhage",
    "infarct",
    "normal",
    "calcification",
    "cyst",
    "effusion",
]
_FIRST_NAMES = ["Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Henry"]
_LAST_NAMES = ["Smith", "Jones", "Lee", "Chen", "Patel", "Brown", "Wilson", "Davis"]
_SUBSPECIALTIES = [
    "body",
    "neuroradiology",
    "musculoskeletal",
    "breast",
    "cardiovascular",
    "nuclear",
    "pediatric",
    "general",
]
_GROUPS = ["Group A", "Group B", "Group C"]


def generate_reviewers(count: int = 8) -> list[Reviewer]:
    reviewers: list[Reviewer] = []
    for i in range(count):
        first = random.choice(_FIRST_NAMES)
        last = random.choice(_LAST_NAMES)
        reviewers.append(
            Reviewer(
                reviewer_id=f"R{100 + i:03d}",
                name=f"Dr. {first} {last}",
                subspecialty=random.choice(_SUBSPECIALTIES),
                group_name=random.choice(_GROUPS),
            )
        )
    return reviewers


def generate_reviews(
    reviewers: list[Reviewer],
    count: int = 100,
    score_system: str = "radpeer",
    start_date: date = date(2024, 1, 1),
    end_date: date = date(2024, 12, 31),
) -> list[PeerReview]:
    reviews: list[PeerReview] = []
    scores = _RADPEER_SCORES if score_system == "radpeer" else _STANDARD_SCORES
    date_range = (end_date - start_date).days

    # Weight scores: most are agreements (1/agree), some discrepancies
    score_weights = _get_score_weights(score_system)

    for i in range(count):
        reviewer = random.choice(reviewers)
        peers = [r for r in reviewers if r.reviewer_id != reviewer.reviewer_id]
        reviewee = random.choice(peers) if peers else reviewer

        score = random.choices(scores, weights=score_weights, k=1)[0]
        rd = start_date + timedelta(days=random.randint(0, date_range))

        reviews.append(
            PeerReview(
                review_id=f"REV{2024000 + i:04d}",
                reviewer_id=reviewer.reviewer_id,
                reviewee_id=reviewee.reviewer_id,
                case_id=f"CASE{random.randint(1000, 9999)}",
                score=score,
                score_system=score_system,
                review_date=rd,
                modality=random.choice(_MODALITIES),
                body_part=random.choice(_BODY_PARTS),
                finding_type=random.choice(_FINDING_TYPES),
                comment=_generate_comment(score, score_system),
            )
        )

    return reviews


def generate_demo_data(
    reviewer_count: int = 8,
    review_count: int = 100,
    score_system: str = "radpeer",
) -> tuple[list[Reviewer], list[PeerReview]]:
    reviewers = generate_reviewers(reviewer_count)
    reviews = generate_reviews(reviewers, review_count, score_system)
    return reviewers, reviews


def _get_score_weights(score_system: str) -> list[float]:
    if score_system == "radpeer":
        return [60, 20, 10, 10]
    return [60, 20, 20]


def _generate_comment(score: str, score_system: str) -> str:
    if score_system == "radpeer":
        if score == "1":
            return random.choice(["", "Agree with findings.", "Good study."])
        return random.choice(
            [
                "Missed small nodule.",
                "Disagree with interpretation.",
                "Should have been called.",
                "Subtle finding, easy to miss.",
                "Different interpretation.",
            ]
        )
    if score == "agree":
        return random.choice(["", "Agree.", "Concur."])
    return random.choice(
        [
            "Missed finding.",
            "Discrepancy in interpretation.",
            "Different conclusion.",
        ]
    )
