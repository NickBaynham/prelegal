# PreLegal

A SaaS for drafting legal agreements from open-source templates. V1 supports the
Common Paper Mutual Non-Disclosure Agreement; additional templates are
catalogued in [`catalog.json`](catalog.json) and will be wired into the UI in
future iterations.

## Architecture

- **Backend:** FastAPI service backed by SQLite. Owns rendering and persistence.
- **Frontend:** Next.js 16 (App Router) UI. Talks to the backend over HTTP.
- **Docker Compose:** runs the two services together with a named SQLite volume
  so data survives container restarts.

```
prelegal/
├── backend/      # FastAPI + SQLite (pdm)
├── frontend/     # Next.js 16 (App Router, TypeScript)
├── templates/    # Markdown legal templates (Common Paper)
├── catalog.json  # Catalog of available templates
├── scripts/      # Per-OS docker start/stop helpers
└── Makefile      # Dev tasks (setup, lint, test, build, run, docker-up/down)
```

## Quick start (Docker)

```
make docker-up
```

- Frontend: <http://localhost:3000>
- Backend:  <http://localhost:8000>
- API docs: <http://localhost:8000/docs>

Stop with `make docker-down`. SQLite data lives in the `prelegal_data` volume.

## Local development

Install dependencies once:

```
make setup
```

Run both services with hot reload (no Docker):

```
make run
```

Run all tests:

```
make test            # backend pytest + frontend vitest
make frontend-test-e2e   # Playwright (requires `npx playwright install chromium` once)
```

Lint:

```
make lint
```

## Configuration

Copy `.env.example` to `.env` and adjust as needed. Variables consumed at
runtime:

| Variable             | Component | Default                  | Purpose                                  |
| -------------------- | --------- | ------------------------ | ---------------------------------------- |
| `DATABASE_PATH`      | backend   | `backend/data/prelegal.db` | SQLite file location                     |
| `TEMPLATES_DIR`      | backend   | `templates/`             | Markdown template root                   |
| `CATALOG_PATH`       | backend   | `catalog.json`           | Catalog descriptor                       |
| `CORS_ORIGINS`       | backend   | `http://localhost:3000`  | Comma-separated allow list               |
| `NEXT_PUBLIC_API_URL`| frontend  | `http://localhost:8000`  | Browser-visible backend URL              |
| `INTERNAL_API_URL`   | frontend  | (falls back to public)   | Server-side backend URL (Docker network) |
| `OPENROUTER_API_KEY` | backend   | unset                    | Enables the AI chat assistant (degrades gracefully when unset) |

## License

MIT — see [LICENSE](LICENSE). Document templates remain under the original
Common Paper CC BY 4.0 license.

## Further reading

- [Backend service](backend/README.md)
- [Change log](CHANGELOG.md)
- [Roadmap / TODO](TODO.md)
