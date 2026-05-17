.PHONY: dev dev-down unit e2e e2e-reset

BACKEND_DIR := backend
# Interpolate POSTGRES_* the same way as when compose lived under backend/
COMPOSE_DEV := docker compose --env-file $(BACKEND_DIR)/.env
# Separate project so e2e `down -v` never touches dev postgres_data
COMPOSE_E2E := docker compose -p leap-e2e --env-file $(BACKEND_DIR)/.env -f docker-compose.yml -f docker-compose.test.yml

# Must match postgres_test credentials (see backend/.env.example)
E2E_DB_URL := postgresql+asyncpg://leap:leap@localhost:5433/leap_test

start:
	$(COMPOSE_DEV) up -d

stop:
	$(COMPOSE_DEV) down

unit:
	cd $(BACKEND_DIR) && uv run pytest tests/unit/ -v

e2e:
	$(COMPOSE_E2E) up -d postgres_test --wait && \
	( cd $(BACKEND_DIR) && POSTGRES_CONNECTION_STRING=$(E2E_DB_URL) uv run alembic upgrade head && uv run pytest tests/e2e/ -v ); \
	e2e_exit=$$?; \
	$(COMPOSE_E2E) down; \
	exit $$e2e_exit

e2e-reset:
	$(COMPOSE_E2E) down -v
	@$(MAKE) e2e
