import pytest

import rad_peer_review_analytics.cli as cli
from rad_peer_review_analytics.analytics import AnalyticsEngine


@pytest.fixture(autouse=True)
def _reset_cli_globals():
    cli._reviews = []
    cli._reviewers = {}
    cli._engine = AnalyticsEngine()
    yield
