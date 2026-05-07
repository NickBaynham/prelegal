# TODO

## Next up
- Wire the catalog into the UI so users can pick a template (currently the form
  hard-codes the Mutual NDA).
- Implement chat-driven field filling using the Cerebras / OpenRouter skill.
- Add authentication and per-user document scoping (V1 is single-user).

## Performance / hardening (deferred from SCRUM-4 review)
- `repo.get_document_detail` makes two SQLite round-trips (`get_document`
  then `get_latest_version`); replace with a single JOIN matching the
  `list_documents` pattern when traffic warrants.
- `render._load_template` uses an `lru_cache` keyed by path string and never
  invalidates. Templates are deploy-time artifacts today, but if we let
  users hot-edit them via a bind mount we will need an mtime-keyed cache
  or to drop the cache entirely.
- `Content-Disposition` filename in the PDF route is not RFC 5987 encoded;
  document titles containing a `"` will produce a malformed header.

## Coverage gaps
- No frontend lint config beyond `next lint` defaults.
- Playwright suite covers the happy path only — add error-state and validation
  scenarios.
- Backend has no test for the `/catalog` 404 path (catalog file missing).

## Operational
- Decide how to expose `OPENROUTER_API_KEY` to the backend container at
  deployment time (currently optional, only required when AI features land).
- Add Alembic (or equivalent) when the schema grows beyond two tables.
