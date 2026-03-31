.PHONY: help dev dev-down prod prod-down logs migrate makemigration seed ollama-pull test

help:
	@echo "NovaDesc — available commands:"
	@echo "  make dev               Start in development mode (hot reload)"
	@echo "  make dev-down          Stop development containers"
	@echo "  make prod              Start in production mode"
	@echo "  make prod-down         Stop production containers"
	@echo "  make logs              Tail all logs"
	@echo "  make migrate           Apply all pending migrations"
	@echo "  make makemigration m=  Generate new migration (e.g. make makemigration m=add_users)"
	@echo "  make seed              Seed initial admin user"
	@echo "  make ollama-pull       Pull default LLM + embed models into Ollama"

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile with-ollama up --build

dev-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

prod:
	docker compose --env-file .env --profile with-ollama up -d --build

prod-down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec backend alembic upgrade head

makemigration:
	docker compose exec backend alembic revision --autogenerate -m "$(m)"

seed:
	docker compose exec backend python -m scripts.seed_admin

ollama-pull:
	docker compose exec ollama ollama pull llama3
	docker compose exec ollama ollama pull nomic-embed-text

test:
	docker compose exec backend pytest --tb=short -q
