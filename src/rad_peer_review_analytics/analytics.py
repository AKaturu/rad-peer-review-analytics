from __future__ import annotations

from collections import defaultdict
from typing import Any

from rad_peer_review_analytics.models import (
    AnalyticsReport,
    BodyPartStats,
    GroupStats,
    ModalityStats,
    MonthlyTrend,
    PeerReview,
    Reviewer,
    ReviewerStats,
)
from rad_peer_review_analytics.scoring import get_score_weight, is_discrepant, is_major_discrepant


class AnalyticsEngine:
    def __init__(self) -> None:
        self.reviews: list[PeerReview] = []
        self.reviewers: dict[str, Reviewer] = {}

    def load(self, reviews: list[PeerReview], reviewers: list[Reviewer] | None = None) -> None:
        if not isinstance(reviews, list) or not all(isinstance(r, PeerReview) for r in reviews):
            raise TypeError("reviews must be a list of PeerReview objects")
        self.reviews = reviews
        if reviewers:
            self.reviewers = {r.reviewer_id: r for r in reviewers}

    def generate_report(self) -> AnalyticsReport:
        report = AnalyticsReport()
        report.total_reviews = len(self.reviews)
        report.total_reviewers = (
            len(self.reviewers) if self.reviewers else self._count_unique_reviewers()
        )

        if not self.reviews:
            return report

        dates = [r.review_date for r in self.reviews if r.review_date]
        if dates:
            report.date_range = f"{min(dates)} to {max(dates)}"

        report.reviewer_stats = self._reviewer_stats()
        report.group_stats = self._group_stats()
        report.modality_stats = self._modality_stats()
        report.body_part_stats = self._body_part_stats()
        report.monthly_trends = self._monthly_trends()

        total = len(self.reviews)
        disc = sum(1 for r in self.reviews if is_discrepant(r.score, r.score_system))
        major = sum(1 for r in self.reviews if is_major_discrepant(r.score, r.score_system))
        total_weight = sum(get_score_weight(r.score, r.score_system) for r in self.reviews)

        report.overall_agreement_rate = _pct(total - disc, total)
        report.overall_major_discrepancy_rate = _pct(major, total)
        report.overall_avg_score = round(total_weight / total, 3) if total else 0.0

        mod_disc: dict[str, int] = defaultdict(int)
        for r in self.reviews:
            if r.modality and is_discrepant(r.score, r.score_system):
                mod_disc[r.modality] += 1
        sorted_mods = sorted(mod_disc.items(), key=lambda x: x[1], reverse=True)
        report.top_discrepant_modalities = [m for m, _ in sorted_mods[:5]]

        return report

    def _count_unique_reviewers(self) -> int:
        ids: set[str] = set()
        for r in self.reviews:
            if r.reviewer_id:
                ids.add(r.reviewer_id)
            if r.reviewee_id:
                ids.add(r.reviewee_id)
        return len(ids)

    def _reviewer_stats(self) -> list[ReviewerStats]:
        stats_map: dict[str, dict[str, Any]] = {}

        for rev in self.reviews:
            for pid in (rev.reviewer_id, rev.reviewee_id):
                if pid and pid not in stats_map:
                    info = self.reviewers.get(pid, Reviewer(reviewer_id=pid))
                    stats_map[pid] = {
                        "reviewer_id": pid,
                        "name": info.name,
                        "subspecialty": info.subspecialty,
                        "group_name": info.group_name,
                        "total_reviews": 0,
                        "total_as_reviewer": 0,
                        "total_as_reviewee": 0,
                        "agreement_count": 0,
                        "minor_discrepancy_count": 0,
                        "major_discrepancy_count": 0,
                        "scores": [],
                    }

        for rev in self.reviews:
            s = get_score_weight(rev.score, rev.score_system)

            if rev.reviewer_id in stats_map:
                stats_map[rev.reviewer_id]["total_reviews"] += 1
                stats_map[rev.reviewer_id]["total_as_reviewer"] += 1
                stats_map[rev.reviewer_id]["scores"].append(s)

            if rev.reviewee_id in stats_map:
                stats_map[rev.reviewee_id]["total_reviews"] += 1
                stats_map[rev.reviewee_id]["total_as_reviewee"] += 1

            if not is_discrepant(rev.score, rev.score_system):
                if rev.reviewer_id in stats_map:
                    stats_map[rev.reviewer_id]["agreement_count"] += 1
            else:
                if is_major_discrepant(rev.score, rev.score_system):
                    if rev.reviewer_id in stats_map:
                        stats_map[rev.reviewer_id]["major_discrepancy_count"] += 1
                else:
                    if rev.reviewer_id in stats_map:
                        stats_map[rev.reviewer_id]["minor_discrepancy_count"] += 1

        results: list[ReviewerStats] = []
        for data in stats_map.values():
            total_rev = data["total_reviews"]
            total_as_reviewer = data["total_as_reviewer"]
            scores = data["scores"]
            ag = data["agreement_count"]
            md = data["major_discrepancy_count"]
            avg = sum(scores) / len(scores) if scores else 0.0

            results.append(
                ReviewerStats(
                    reviewer_id=data["reviewer_id"],
                    name=data["name"],
                    subspecialty=data["subspecialty"],
                    group_name=data["group_name"],
                    total_reviews=total_rev,
                    total_as_reviewer=data["total_as_reviewer"],
                    total_as_reviewee=data["total_as_reviewee"],
                    agreement_count=ag,
                    minor_discrepancy_count=data["minor_discrepancy_count"],
                    major_discrepancy_count=md,
                    agreement_rate=round(_pct(ag, total_as_reviewer), 3),
                    major_discrepancy_rate=round(_pct(md, total_as_reviewer), 3),
                    avg_score=round(avg, 3),
                    trend_direction=self._compute_trend(data["reviewer_id"]),
                )
            )

        results.sort(key=lambda x: x.agreement_rate)
        return results

    def _compute_trend(self, reviewer_id: str) -> str:
        reviewer_reviews = [
            r for r in self.reviews if r.reviewer_id == reviewer_id and r.review_date
        ]
        if len(reviewer_reviews) < 4:
            return "stable"

        reviewer_reviews.sort(key=lambda r: r.review_date or "")
        half = len(reviewer_reviews) // 2
        first_half = reviewer_reviews[:half]
        second_half = reviewer_reviews[half:]

        first_agreement = sum(1 for r in first_half if not is_discrepant(r.score, r.score_system))
        second_agreement = sum(1 for r in second_half if not is_discrepant(r.score, r.score_system))
        first_rate = _pct(first_agreement, len(first_half))
        second_rate = _pct(second_agreement, len(second_half))

        if second_rate > first_rate + 0.05:
            return "improving"
        if second_rate < first_rate - 0.05:
            return "declining"
        return "stable"

    def _group_stats(self) -> list[GroupStats]:
        groups: dict[str, list[PeerReview]] = defaultdict(list)
        for rev in self.reviews:
            info = self.reviewers.get(rev.reviewer_id)
            group = info.group_name if info and info.group_name else "Unassigned"
            groups[group].append(rev)

        groups.setdefault("Unassigned", [])

        results: list[GroupStats] = []
        for group_name, reviews in groups.items():
            if not reviews:
                continue
            members = set()
            for r in reviews:
                if r.reviewer_id:
                    members.add(r.reviewer_id)
                if r.reviewee_id:
                    members.add(r.reviewee_id)
            total = len(reviews)
            disc = sum(1 for r in reviews if is_discrepant(r.score, r.score_system))
            major = sum(1 for r in reviews if is_major_discrepant(r.score, r.score_system))
            avg = sum(get_score_weight(r.score, r.score_system) for r in reviews) / total

            results.append(
                GroupStats(
                    group_name=group_name,
                    reviewer_count=len(members),
                    total_reviews=total,
                    agreement_rate=round(_pct(total - disc, total), 3),
                    major_discrepancy_rate=round(_pct(major, total), 3),
                    avg_score=round(avg, 3),
                )
            )

        results.sort(key=lambda x: x.agreement_rate)
        return results

    def _modality_stats(self) -> list[ModalityStats]:
        mods: dict[str, list[PeerReview]] = defaultdict(list)
        for rev in self.reviews:
            if rev.modality:
                mods[rev.modality].append(rev)

        results: list[ModalityStats] = []
        for modality, reviews in mods.items():
            total = len(reviews)
            disc = sum(1 for r in reviews if is_discrepant(r.score, r.score_system))
            major = sum(1 for r in reviews if is_major_discrepant(r.score, r.score_system))
            avg = sum(get_score_weight(r.score, r.score_system) for r in reviews) / total
            results.append(
                ModalityStats(
                    modality=modality,
                    total_reviews=total,
                    agreement_rate=round(_pct(total - disc, total), 3),
                    major_discrepancy_rate=round(_pct(major, total), 3),
                    avg_score=round(avg, 3),
                )
            )

        results.sort(key=lambda x: x.major_discrepancy_rate, reverse=True)
        return results

    def _body_part_stats(self) -> list[BodyPartStats]:
        parts: dict[str, list[PeerReview]] = defaultdict(list)
        for rev in self.reviews:
            if rev.body_part:
                parts[rev.body_part].append(rev)

        results: list[BodyPartStats] = []
        for body_part, reviews in parts.items():
            total = len(reviews)
            disc = sum(1 for r in reviews if is_discrepant(r.score, r.score_system))
            major = sum(1 for r in reviews if is_major_discrepant(r.score, r.score_system))
            results.append(
                BodyPartStats(
                    body_part=body_part,
                    total_reviews=total,
                    agreement_rate=round(_pct(total - disc, total), 3),
                    major_discrepancy_rate=round(_pct(major, total), 3),
                )
            )

        results.sort(key=lambda x: x.major_discrepancy_rate, reverse=True)
        return results

    def _monthly_trends(self) -> list[MonthlyTrend]:
        months: dict[str, list[PeerReview]] = defaultdict(list)
        for rev in self.reviews:
            if rev.review_date:
                key = rev.review_date.strftime("%Y-%m")
                months[key].append(rev)

        results: list[MonthlyTrend] = []
        for ym in sorted(months):
            reviews = months[ym]
            total = len(reviews)
            ag = sum(1 for r in reviews if not is_discrepant(r.score, r.score_system))
            major = sum(1 for r in reviews if is_major_discrepant(r.score, r.score_system))
            results.append(
                MonthlyTrend(
                    year_month=ym,
                    total_reviews=total,
                    agreement_count=ag,
                    agreement_rate=round(_pct(ag, total), 3),
                    major_discrepancy_count=major,
                    major_discrepancy_rate=round(_pct(major, total), 3),
                )
            )

        return results


def _pct(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
