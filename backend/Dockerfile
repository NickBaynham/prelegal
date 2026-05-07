FROM python:3.13-slim AS builder

RUN pip install --no-cache-dir pdm==2.26.8

WORKDIR /build
COPY pyproject.toml pdm.lock ./
RUN pdm export --prod --without-hashes -o requirements.txt

FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY --from=builder /build/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY prelegal/ ./prelegal/

ENV DATABASE_PATH=/data/prelegal.db \
    TEMPLATES_DIR=/app/templates \
    CATALOG_PATH=/app/catalog.json \
    CORS_ORIGINS=http://localhost:3000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request, sys; sys.exit(0) if urllib.request.urlopen('http://localhost:8000/health').status == 200 else sys.exit(1)" || exit 1

CMD ["uvicorn", "prelegal.main:app", "--host", "0.0.0.0", "--port", "8000"]
