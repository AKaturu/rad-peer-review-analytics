from importlib.metadata import version

from rad_peer_review_analytics import __version__


def test_package_version_matches_distribution_metadata() -> None:
    assert __version__ == version("rad-peer-review-analytics")
