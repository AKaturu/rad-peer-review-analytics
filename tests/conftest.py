import pytest


@pytest.fixture(autouse=True)
def _reset_cli_globals():
    import rad_peer_review_analytics.cli as cli

    cli._reviews = []
    cli._reviewers = {}
    cli._engine = cli.AnalyticsEngine()
    yield
