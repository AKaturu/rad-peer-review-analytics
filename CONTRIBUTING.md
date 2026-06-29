# Contributing

Contributions are welcome when they keep the project synthetic-first and reproducible.

## Local Setup

```bash
git clone https://github.com/AKaturu/rad-peer-review-analytics.git
cd rad-peer-review-analytics
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
```

## Guidelines

- Use synthetic or properly de-identified examples only.
- Add or update tests for behavior changes.
- Keep public documentation clear about evidence status and limitations.
- Do not add patient-level data, reviewer identities, credentials, or institution-specific private reports.
