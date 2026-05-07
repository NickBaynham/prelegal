.PHONY: help setup lint test build run docker-up docker-down clean \
        backend-setup backend-lint backend-test \
        frontend-setup frontend-lint frontend-test frontend-test-e2e frontend-build

# Detect host OS for the docker start/stop scripts.
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    START_SCRIPT := scripts/start-mac.sh
    STOP_SCRIPT  := scripts/stop-mac.sh
else ifeq ($(UNAME_S),Linux)
    START_SCRIPT := scripts/start-linux.sh
    STOP_SCRIPT  := scripts/stop-linux.sh
else
    START_SCRIPT := UNSUPPORTED
    STOP_SCRIPT  := UNSUPPORTED
endif

help:
	@echo "PreLegal — common tasks"
	@echo "  make setup        Install backend (pdm) and frontend (npm) dependencies"
	@echo "  make lint         Lint backend (ruff) and frontend (next lint)"
	@echo "  make test         Run backend pytest and frontend vitest"
	@echo "  make build        Build frontend bundle and Docker images"
	@echo "  make run          Run backend + frontend locally (no Docker)"
	@echo "  make docker-up    Start the full stack via docker compose"
	@echo "  make docker-down  Stop the full stack"

setup: backend-setup frontend-setup

backend-setup:
	cd backend && pdm install

frontend-setup:
	cd frontend && npm install

lint: backend-lint frontend-lint

backend-lint:
	cd backend && pdm run ruff check .

frontend-lint:
	cd frontend && npm run lint --silent || true

test: backend-test frontend-test

backend-test:
	cd backend && pdm run pytest

frontend-test:
	cd frontend && npm test --silent

frontend-test-e2e:
	cd frontend && npm run test:e2e --silent

build: frontend-build
	docker compose build

frontend-build:
	cd frontend && npm run build

run:
	@echo "Starting backend on :8000 and frontend on :3000 (Ctrl-C to stop)"
	@trap 'kill 0' INT TERM EXIT; \
		(cd backend && pdm run uvicorn prelegal.main:app --reload --port 8000) & \
		(cd frontend && npm run dev) & \
		wait

docker-up:
ifeq ($(START_SCRIPT),UNSUPPORTED)
	@echo "Unsupported OS for auto-dispatch. On Windows run: pwsh scripts/start-windows.ps1"; exit 1
else
	./$(START_SCRIPT)
endif

docker-down:
ifeq ($(STOP_SCRIPT),UNSUPPORTED)
	@echo "Unsupported OS for auto-dispatch. On Windows run: pwsh scripts/stop-windows.ps1"; exit 1
else
	./$(STOP_SCRIPT)
endif

clean:
	rm -rf backend/data/*.db backend/data/*.db-shm backend/data/*.db-wal
	rm -rf frontend/.next frontend/tests/e2e/.tmp
