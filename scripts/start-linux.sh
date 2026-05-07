#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose up -d --build
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
