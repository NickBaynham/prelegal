# Changelog

## SCRUM-4 — V1 foundation (2026-05-06)

### Added
- FastAPI backend with SQLite persistence (`backend/`).
  - REST endpoints: `/health`, `/catalog`, `/documents` (list/create), `/documents/{id}`, `/documents/{id}/versions` (list/create), `/documents/{id}/versions/{vid}`.
  - Race-safe versioning via `BEGIN IMMEDIATE` on writers.
  - Pydantic v2 models mirror the frontend Zod schema.
  - Cover-page + standard-terms rendering ported from TypeScript to Python.
  - Test coverage: 34 tests (11 render unit, 9 repo unit, 14 API integration).
- Frontend refactored to call the backend over HTTP (`frontend/lib/api.ts`,
  `frontend/lib/repo.ts`). Server actions delegate to backend; rendering and
  persistence removed from the Next.js process.
- Vitest unit tests for the API helper and Zod schema (6 tests).
- Playwright E2E test exercising the full create / view / reload / list flow.
- `Dockerfile` for both services; `docker-compose.yml` with a named SQLite
  volume (`prelegal_data`) so data persists across container restarts.
- `Makefile` with `setup`, `lint`, `test`, `build`, `run`, `docker-up`,
  `docker-down`. `docker-up`/`docker-down` dispatch to the per-OS scripts in
  `scripts/`.
- Per-OS dev scripts: `start-mac.sh`/`stop-mac.sh`, `start-linux.sh`/
  `stop-linux.sh`, `start-windows.ps1`/`stop-windows.ps1`.

### Changed
- README rewritten to reflect the FastAPI + Next.js + Docker layout and to use
  `pdm` and `make` rather than `pip`/`venv`.
- `.env.example` extended with backend and frontend variables.
- Frontend `next.config.ts` now uses `output: "standalone"` for a slimmer
  Docker image.

### Removed
- `frontend/lib/db.ts`, `frontend/lib/render.ts`, `frontend/data/`. Persistence
  and rendering now live in the backend.
- `better-sqlite3` dependency.

## SCRUM-3 — Mutual NDA creator prototype (earlier)

- Initial Next.js prototype with embedded SQLite.

## SCRUM-2 — Common Paper template dataset (earlier)

- 12 markdown templates committed under `templates/`.
