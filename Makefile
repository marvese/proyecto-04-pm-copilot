.DEFAULT_GOAL := help
.PHONY: up down db-init db-reset db-shell logs tools-up tools-down ps verify migrate migrate-down sync-docs sync-jira sync-all help

# Lee .env si existe (para variables en targets que las necesiten)
-include .env
export

# ─────────────────────────────────────────
# Servicios principales (postgres + chromadb)
# ─────────────────────────────────────────

up: ## Arranca PostgreSQL y ChromaDB en segundo plano
	docker compose up -d

down: ## Para y elimina los contenedores (los volúmenes persisten)
	docker compose down

logs: ## Sigue los logs de todos los servicios
	docker compose logs -f

ps: ## Muestra el estado de los contenedores
	docker compose ps

# ─────────────────────────────────────────
# Base de datos
# ─────────────────────────────────────────

db-init: ## Ejecuta scripts/db_init.sql contra PostgreSQL (espera a que esté healthy)
	@echo "Esperando a que PostgreSQL esté listo..."
	@docker compose exec postgres sh -c 'until pg_isready -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -q; do sleep 1; done'
	@echo "Ejecutando DDL..."
	@docker compose exec -T postgres sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"' < scripts/db_init.sql
	@echo "DDL aplicado correctamente."

db-reset: ## Elimina y recrea la base de datos (¡destruye todos los datos!)
	@echo "ADVERTENCIA: esto eliminará todos los datos de la BD."
	@read -p "¿Continuar? [y/N] " ans && [ "$$ans" = "y" ]
	docker compose down -v
	docker compose up -d
	$(MAKE) db-init

db-shell: ## Abre psql interactivo
	docker compose exec postgres psql -U "$(POSTGRES_USER)" -d "$(POSTGRES_DB)"

# ─────────────────────────────────────────
# Herramientas opcionales (pgAdmin)
# ─────────────────────────────────────────

verify: ## Verifica que todos los servicios están listos (PostgreSQL, ChromaDB, Ollama)
	python3 scripts/verify_env.py

migrate: ## Aplica todas las migraciones pendientes (alembic upgrade head)
	cd backend && alembic upgrade head

migrate-down: ## Revierte la última migración (alembic downgrade -1)
	cd backend && alembic downgrade -1

# ─────────────────────────────────────────
# Herramientas opcionales (pgAdmin)
# ─────────────────────────────────────────

tools-up: ## Arranca pgAdmin en http://localhost:5050
	docker compose --profile tools up -d

tools-down: ## Para pgAdmin
	docker compose --profile tools down

# ─────────────────────────────────────────
# Sincronización de documentación
# ─────────────────────────────────────────

sync-docs: ## Sube docs/pending/confluence/*.md a Confluence y los mueve a docs/published/
	python3 scripts/sync_confluence.py

sync-jira: ## Procesa docs/pending/jira/update-tasks.json y actualiza estados en Jira
	python3 scripts/sync_jira_status.py

sync-all: sync-docs sync-jira ## Sincroniza documentación y estados Jira en un solo paso

# ─────────────────────────────────────────
# Ayuda
# ─────────────────────────────────────────

help: ## Muestra esta ayuda
	@echo ""
	@echo "  PM Copilot — comandos disponibles"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo ""
