# AGENTS.md

## Linting

- Always run `ruff check --fix` and `ruff format` on the Python sources **before committing** and after finishing any code change.
- Fix all remaining lint errors (not just auto-fixable ones); do not leave warnings behind.
- Full check: `.venv/bin/ruff check custom_components tests` (must exit 0).
- Also run `pytest` (`.venv/bin/python -m pytest tests/`) and make sure all tests pass before committing.
