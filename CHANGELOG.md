# Changelog

## SCRUM-5 — AI chat-driven Mutual NDA creation (2026-05-07)

### Added
- `/chat` FastAPI endpoint backed by liteLLM via OpenRouter, pinned to the
  Cerebras inference provider (`openrouter/openai/gpt-oss-120b`). Single-turn
  JSON; structured output via `response_format=ChatResponse` (Pydantic).
- New Pydantic models in `backend/prelegal/models.py`: `ChatMessage`,
  `ChatRequest`, `ChatResponse`, `PartialNdaFormValues`, `PartialParty`.
- `backend/prelegal/llm.py` — single `chat_assist` function plus a
  `build_system_prompt` helper that embeds the user's current partial values
  in each turn's system prompt.
- `Settings.openrouter_api_key`. Empty / unset means the AI is disabled and
  `/chat` returns HTTP 503; everything else continues to work.
- Frontend chat client at `/new`: `ChatPanel` + `ChatNdaClient` replace the
  bare `NewNdaClient`. The chat panel and the existing 9-section NdaForm now
  share one `react-hook-form` instance, so AI-extracted values flow into the
  form via `setValue`.
- `frontend/lib/chat.ts`: chat types, `assistChat` API call,
  `applyExtractedValues`, and `snapshotCurrentValues`.
- Test coverage:
  - 10 unit tests for the chat Pydantic models.
  - 3 unit tests for `build_system_prompt`.
  - 4 integration tests for `POST /chat` (503 unset, 200 happy, 422 bad body,
    502 on LLM exception).
  - 8 Vitest unit tests for `applyExtractedValues` / `snapshotCurrentValues`.
  - 2 Playwright E2E tests: AI-fills-then-user-submits, and 503 degraded mode.

### Changed
- `NdaForm` now accepts an optional `form` prop so a parent can lift the
  `useForm` instance and share state with the chat panel; existing edit page
  unchanged.
- `docker-compose.yml` threads `OPENROUTER_API_KEY` into the backend service.
- `.env.example` clarifies that the AI key is optional and documents the
  degraded behaviour when unset.
- `DateString` now validates calendar correctness (e.g. rejects `2026-02-30`),
  not just the regex shape. Tightens `effectiveDate` end-to-end.

### Removed
- `frontend/components/NewNdaClient.tsx` (superseded by `ChatNdaClient`).

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
