# agentUniverse Admin Module Contribution Guide

This guide covers the `agentuniverse_product/service/admin_service` module only.
For project-wide contribution rules, see the repository root `CONTRIBUTING.md`.

## Local Setup

1. Use Python 3.10.
2. Install dependencies with Poetry from the `agentUniverse/` repository root:
   ```bash
   poetry install
   ```
3. Work from the repository root so imports and test paths resolve consistently.

## Run Tests

Use the admin-focused test targets while iterating:

```bash
poetry run pytest tests/test_agentuniverse/unit/agent_serve/test_admin_*.py -q
poetry run pytest tests/test_agentuniverse/unit/agent_serve/test_admin_api_integration.py -q
```

For broader validation before sending a PR:

```bash
poetry run pytest tests/ -q
```

## Branches, Commits, and PRs

- Branch names: `feat/admin-...`, `fix/admin-...`, `test/admin-...`, `docs/admin-...`
- Commit messages: `type(admin): short summary`
- PR title: keep the `type(admin): ...` prefix aligned with the main change
- PR body: include Summary, Changes, Test Plan, Checklist, and issue links such as `Relates to #568` when applicable

## Code Style

- Follow PEP 8 and the existing Google-style docstring pattern used in the repository.
- Keep admin changes small and module-scoped.
- Prefer the existing blueprint/service/DTO layout over introducing new abstractions.
- Do not add dependencies unless the change cannot be completed without them.
- Keep YAML config and Python service code paired and consistent.

