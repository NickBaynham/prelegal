# prelegal-backend

FastAPI service backing the PreLegal SaaS. Persists drafted legal documents to SQLite.

## Local development

```
pdm install
pdm run uvicorn prelegal.main:app --reload --port 8000
```

API at http://localhost:8000, interactive docs at http://localhost:8000/docs.

## Tests

```
pdm run pytest
```

## Configuration

| Variable        | Default                | Purpose                      |
| --------------- | ---------------------- | ---------------------------- |
| `DATABASE_PATH` | `./data/prelegal.db`   | SQLite file location         |
| `TEMPLATES_DIR` | `../templates`         | Markdown template root       |
| `CATALOG_PATH`  | `../catalog.json`      | Document catalog descriptor  |
| `CORS_ORIGINS`  | `http://localhost:3000`| Comma-separated allow list   |
