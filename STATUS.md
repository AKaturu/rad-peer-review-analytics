# rad-peer-review-analytics — Project Status

## Current Release

**v0.1.0** — Initial release providing RADPEER and standard score-system peer review tracking, scoring, analytics, and CLI reporting.

## Implemented Features

- RADPEER (1/2/3a/3b) and standard (agree/minor/major/not actionable) score systems with automatic conversion
- CSV import with flexible column-name matching and date-format auto-detection
- Reviewer, group, modality, body-part, and monthly-trend analytics
- Trend-direction detection (improving / declining / stable)
- Multi-file CSV export and single-file JSON export
- Typer-based CLI with 8 commands
- Reproducible synthetic demo data and demo media generation
- 14 Pydantic models, 3 StrEnum types
- CI: ruff, mypy, pytest on Python 3.11+

## Quality Gates

- All tests pass on Python 3.11 and 3.12
- No ruff violations
- No mypy errors
- Coverage reported via pytest-cov

## Known Issues

- None at this release
