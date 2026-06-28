from rad_peer_review_analytics.models import PeerReview, Reviewer
from rad_peer_review_analytics.synthetic import (
    generate_demo_data,
    generate_reviewers,
    generate_reviews,
)


class TestGenerateReviewers:
    def test_default_count(self):
        reviewers = generate_reviewers()
        assert len(reviewers) == 8
        for r in reviewers:
            assert r.reviewer_id.startswith("R")
            assert r.name.startswith("Dr.")

    def test_custom_count(self):
        reviewers = generate_reviewers(3)
        assert len(reviewers) == 3

    def test_unique_ids(self):
        reviewers = generate_reviewers(20)
        ids = [r.reviewer_id for r in reviewers]
        assert len(set(ids)) == 20


class TestGenerateReviews:
    def test_default_count(self):
        reviewers = generate_reviewers(5)
        reviews = generate_reviews(reviewers)
        assert len(reviews) == 100

    def test_custom_count(self):
        reviewers = generate_reviewers(3)
        reviews = generate_reviews(reviewers, 10)
        assert len(reviews) == 10

    def test_radpeer_scores(self):
        reviewers = generate_reviewers(3)
        reviews = generate_reviews(reviewers, 50, score_system="radpeer")
        for r in reviews:
            assert r.score in ("1", "2", "3a", "3b")
            assert r.score_system == "radpeer"

    def test_standard_scores(self):
        reviewers = generate_reviewers(3)
        reviews = generate_reviews(reviewers, 50, score_system="standard")
        for r in reviews:
            assert r.score in ("agree", "minor_discrepancy", "major_discrepancy")
            assert r.score_system == "standard"

    def test_date_range(self):
        from datetime import date

        reviewers = generate_reviewers(3)
        start = date(2024, 1, 1)
        end = date(2024, 3, 31)
        reviews = generate_reviews(reviewers, 30, start_date=start, end_date=end)
        for r in reviews:
            assert r.review_date is not None
            assert start <= r.review_date <= end

    def test_reviewer_used_as_reviewee(self):
        reviewers = generate_reviewers(3)
        reviews = generate_reviews(reviewers, 20)
        for r in reviews:
            assert r.reviewer_id in {rev.reviewer_id for rev in reviewers}
            # reviewee should be different from reviewer (if possible)
            if len(reviewers) > 1:
                assert r.reviewer_id != r.reviewee_id

    def test_modality_and_body_part_set(self):
        reviewers = generate_reviewers(3)
        reviews = generate_reviews(reviewers, 10)
        for r in reviews:
            assert r.modality
            assert r.body_part

    def test_custom_date_range(self):
        from datetime import date

        reviewers = generate_reviewers(3)
        start = date(2023, 6, 1)
        end = date(2023, 8, 31)
        reviews = generate_reviews(reviewers, 10, start_date=start, end_date=end)
        for r in reviews:
            assert start <= r.review_date <= end


class TestGenerateDemoData:
    def test_returns_tuple(self):
        result = generate_demo_data()
        assert len(result) == 2
        reviewers, reviews = result
        assert isinstance(reviewers, list)
        assert isinstance(reviews, list)
        assert all(isinstance(r, Reviewer) for r in reviewers)
        assert all(isinstance(r, PeerReview) for r in reviews)

    def test_counts(self):
        reviewers, reviews = generate_demo_data(reviewer_count=5, review_count=25)
        assert len(reviewers) == 5
        assert len(reviews) == 25

    def test_standard_system(self):
        _reviewers, reviews = generate_demo_data(
            reviewer_count=3, review_count=10, score_system="standard"
        )
        for r in reviews:
            assert r.score_system == "standard"
