# Variables
PYTHON_VERSION := 3.8
POETRY_VERSION := 1.4.2
DOCKER := docker
FRONTEND_PORT := 3030
BACKEND_PORT := 8080

# Colors for terminal output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

.PHONY: help install clean dev test lint format docker-up docker-down frontend backend all

help: ## Display this help message
	@echo "$(CYAN)Algo Trading Dashboard Management Commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(CYAN)%-30s$(NC) %s\n", $$1, $$2}'

install: ## Install project dependencies
	@echo "$(GREEN)Installing Poetry...$(NC)"
	@curl -sSL https://install.python-poetry.org | python3 -
	@echo "$(GREEN)Installing Python dependencies...$(NC)"
	@poetry install
	@echo "$(GREEN)Installing frontend dependencies...$(NC)"
	@cd frontend && npm install
	@echo "$(GREEN)Setting up frontend environment...$(NC)"
	@cp frontend/.env.template frontend/.env

clean: docker-down ## Clean up the project (remove containers, node_modules, etc.)
	@echo "$(GREEN)Cleaning up project...$(NC)"
	@rm -rf frontend/node_modules
	@rm -rf frontend/build
	@rm -rf .pytest_cache
	@rm -rf __pycache__
	@rm -rf .coverage
	@find . -type d -name "__pycache__" -exec rm -rf {} +

dev: docker-up ## Start development environment
	@echo "$(GREEN)Starting development environment...$(NC)"
	@make -j2 frontend backend

docker-up: ## Start Docker containers
	@echo "$(GREEN)Starting Docker containers...$(NC)"
	@$(DOCKER) compose up -d

docker-down: ## Stop Docker containers
	@echo "$(GREEN)Stopping Docker containers...$(NC)"
	@$(DOCKER) compose down

frontend: ## Start frontend development server
	@echo "$(GREEN)Starting frontend server on port $(FRONTEND_PORT)...$(NC)"
	@cd frontend && PORT=$(FRONTEND_PORT) npm start

backend: ## Start backend development server
	@echo "$(GREEN)Starting backend server on port $(BACKEND_PORT)...$(NC)"
	@poetry run uvicorn src.infrastructure.api.main:app --reload --port $(BACKEND_PORT)

test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	@poetry run pytest

lint: ## Run linting
	@echo "$(GREEN)Running linters...$(NC)"
	@poetry run flake8 src tests
	@poetry run mypy src tests

format: ## Format code
	@echo "$(GREEN)Formatting code...$(NC)"
	@poetry run black src tests

docker-build: ## Build Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	@$(DOCKER) compose build

docker-logs: ## View Docker container logs
	@echo "$(GREEN)Viewing Docker logs...$(NC)"
	@$(DOCKER) compose logs -f

docker-ps: ## List running containers
	@echo "$(GREEN)Listing containers...$(NC)"
	@$(DOCKER) compose ps

docker-clean: docker-down ## Clean Docker resources
	@echo "$(GREEN)Cleaning Docker resources...$(NC)"
	@$(DOCKER) system prune -f

setup: install docker-build ## Initial project setup
	@echo "$(GREEN)Project setup complete!$(NC)"
	@echo "$(YELLOW)Run 'make dev' to start development environment$(NC)"
	@echo "$(YELLOW)Frontend will be available at http://localhost:$(FRONTEND_PORT)$(NC)"
	@echo "$(YELLOW)Backend API will be available at http://localhost:$(BACKEND_PORT)$(NC)"

all: setup ## Setup and start everything
	@make dev
