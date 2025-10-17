.PHONY: help setup up down restart logs logs-bot logs-memory logs-astrology ps health build clean backup restore

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

setup: ## Initial setup - create .env from template
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file. Please edit it with your configuration."; \
	else \
		echo "⚠️  .env file already exists. Skipping."; \
	fi

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

down-volumes: ## Stop all services and remove volumes (⚠️  deletes data)
	docker-compose down -v

restart: ## Restart all services
	docker-compose restart

restart-bot: ## Restart bot service only
	docker-compose restart bot

restart-memory: ## Restart memory service only
	docker-compose restart memory-service

restart-astrology: ## Restart astrology services only
	docker-compose restart astrology-api astrology-mcp

logs: ## View logs from all services
	docker-compose logs -f

logs-bot: ## View bot logs
	docker-compose logs -f bot

logs-memory: ## View memory service logs
	docker-compose logs -f memory-service

logs-astrology: ## View astrology service logs
	docker-compose logs -f astrology-api astrology-mcp

logs-postgres: ## View PostgreSQL logs
	docker-compose logs -f postgres

logs-redis: ## View Redis logs
	docker-compose logs -f redis

logs-rabbitmq: ## View RabbitMQ logs
	docker-compose logs -f rabbitmq

ps: ## Show running services
	docker-compose ps

health: ## Check health of all services
	@echo "Service Health Status:"
	@docker-compose ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"

build: ## Rebuild all services
	docker-compose build

build-bot: ## Rebuild bot service
	docker-compose build bot

build-memory: ## Rebuild memory service
	docker-compose build memory-service

build-astrology: ## Rebuild astrology services
	docker-compose build astrology-api astrology-mcp

clean: ## Remove stopped containers and unused images
	docker-compose down
	docker system prune -f

shell-bot: ## Open shell in bot container
	docker-compose exec bot /bin/bash

shell-memory: ## Open shell in memory container
	docker-compose exec memory-service /bin/sh

shell-postgres: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

shell-redis: ## Open Redis CLI
	docker-compose exec redis redis-cli -a ${REDIS_PASSWORD}

backup: ## Backup PostgreSQL database
	@mkdir -p backups
	@docker-compose exec -T postgres pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Database backed up to backups/backup_$$(date +%Y%m%d_%H%M%S).sql"

restore: ## Restore PostgreSQL database (usage: make restore FILE=backups/backup_20240101_120000.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Please specify backup file: make restore FILE=backups/backup_20240101_120000.sql"; \
		exit 1; \
	fi
	@docker-compose exec -T postgres psql -U ${POSTGRES_USER} ${POSTGRES_DB} < $(FILE)
	@echo "✅ Database restored from $(FILE)"

stats: ## Show resource usage statistics
	docker stats --no-stream

migrate: ## Run database migrations
	docker-compose run --rm bot-init

dev-up: ## Start services with build
	docker-compose up -d --build

dev-logs: ## View logs with timestamps
	docker-compose logs -f --timestamps