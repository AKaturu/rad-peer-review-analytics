# Changelog

## Unreleased

- Pinned every GitHub Action dependency to an immutable commit SHA.
- Added a distribution-metadata contract test to prevent package-version drift.
- Write and read JSON/CSV exports explicitly as UTF-8.
- Corrected author attribution to Abinav Katuru.
- Published PEP 561 typing metadata and removed blanket mypy import suppression.
- Added Python 3.13 CI coverage and modern SPDX package metadata.

## v0.1.0 (2026-06-28)

- Initial release with RADPEER and standard score systems
- CSV import with flexible column-name matching
- Reviewer, group, modality, body-part, and monthly-trend analytics
- Trend-direction detection
- Multi-file CSV and single-file JSON export
- Typer-based CLI with 8 commands
- Reproducible synthetic demo data and demo media generation
