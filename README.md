# Viaduct Echo Backend

News aggregation for Greater Manchester with a Python backend, FastAPI REST API, and optional publishing to GitHub Pages. Android and iOS apps live in this monorepo.

– Python 3.13 • FastAPI • SQLAlchemy • PostgreSQL • Black • Ruff • pre-commit • uv

## Overview
- Fetches articles from BBC and Manchester Evening News (RSS) and Nub News (scrape).
- Extracts content, generates AI summaries (OpenAI), stores in Postgres.
- Exposes REST API and can publish posts to a Jekyll site on GitHub Pages.
- Developer experience: pre-commit hooks, Ruff + Black, Bandit, tests, Makefile, Docker.

## What’s New
- Migrated linting to Ruff (replaced Flake8 + isort). Black remains the formatter.
- Centralized API mappers to remove duplication and keep responses consistent.
- Database ops use a small retry helper + safer MD5 variant (`usedforsecurity=False` fallback).
- Optional `HTTP_TIMEOUT` to add timeouts to outbound requests without changing legacy behavior.
- pre-commit runs Ruff; CI runs Ruff + Black; `.env.example` added.

## Project Layout
```
src/
  api/        # FastAPI app, routes, schemas
  database/   # SQLAlchemy models + operations
  processors/ # AI summarizer, content extraction
  sources/    # BBC/MEN/Nub fetchers
  publishers/ # GitHub Pages publisher
tests/        # API, DB, processors, sources
android-app/  # Kotlin app
ios-app/      # SwiftUI app
```

## Quick Start
Prereqs: Python 3.13+, PostgreSQL 15+, uv

```bash
cp .env.example .env   # add credentials
make dev-setup         # install deps + pre-commit hooks
make run-api           # http://localhost:8000 (docs at /docs)
```

Common tasks
- `make run` – aggregator once/scheduler
- `make test` – run tests
- `make lint` – Ruff + Bandit
- `make format` – Black + import order via Ruff

## Configuration (env)
- `DATABASE_URL` (required): Postgres DSN
- `OPENAI_API_KEY` (optional): enable AI summaries
- `GITHUB_TOKEN`, `GITHUB_REPO`, `GITHUB_BRANCH` (optional): GitHub Pages publishing
- `API_TITLE`, `API_VERSION`, `CORS_ORIGINS` (optional)
- `DEFAULT_PAGE_SIZE`, `MAX_PAGE_SIZE` (optional)
- `HTTP_TIMEOUT` (optional): seconds for outbound requests; unset keeps legacy no-timeout

See `.env.example` for a quick template.

## CI / Quality
- Lint: `ruff check` (includes import sorting). Format: `black`.
- Security: Bandit (informational in CI; enforced in pre-commit).
- Tests: `pytest` with coverage in CI.

## Deployment
- Dockerfiles and compose files included. API runs on port 8000.
- Example: `make docker-build && docker run -p 8000:8000 --env-file .env viaductecho-backend`.

## License
MIT – see `LICENSE`.
