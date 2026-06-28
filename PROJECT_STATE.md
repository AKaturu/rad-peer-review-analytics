# rad-peer-review-analytics - Project State

## Current Status

Complete for the current GitHub presentation pass.

## Completed This Session

- Added reproducible synthetic demo media generation.
- Added README demo GIF, demo regeneration commands, and demo asset policy documentation.
- Added optional `media` dependencies for local asset regeneration.

## Validation

Run before release:

```bash
python -m pip install -e ".[dev,media]"
python scripts/generate_demo_media.py
python -m ruff check .
python -m pytest
```

## Remaining Work

- Cut a version tag to trigger release artifact workflows when ready.
- Keep screenshots and demo media synthetic-only for public GitHub use.
