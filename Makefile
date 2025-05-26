# Makefile
AGENT_NAME=agent_argocd
# Convert agent name to kebab case for Docker image tagging
AGENT_NAME_DASH=$(shell echo $(AGENT_NAME) | tr '_' '-')

.PHONY: \
  build setup-venv activate-venv install run run-acp run-client \
  langgraph-dev help clean clean-pyc clean-venv clean-build-artifacts \
  install-uv install-wfsm verify-a2a-sdk evals \
  run-a2a run-acp-client run-a2a-client run-curl-client \
  build-docker-acp build-docker-acp-tag-and-push \
  check-env lint ruff-fix \
  add-copyright-license-headers

## ========== Setup & Clean ==========

setup-venv:        ## Create the Python virtual environment
	@echo "Setting up virtual environment..."
	@if [ ! -d ".venv" ]; then \
		python3 -m venv .venv && echo "Virtual environment created."; \
	else \
		echo "Virtual environment already exists."; \
	fi
	@echo "To activate manually, run: source .venv/bin/activate"
	@. .venv/bin/activate

clean-pyc:         ## Remove Python bytecode and __pycache__
	@echo "Cleaning up Python bytecode and __pycache__ directories..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + || echo "No __pycache__ directories found."

clean-venv:        ## Remove the virtual environment
	@rm -rf .venv && echo "Virtual environment removed." || echo "No virtual environment found."

clean-build-artifacts: ## Remove dist/, build/, egg-info/
	@echo "Cleaning up build artifacts..."
	@rm -rf dist $(AGENT_NAME).egg-info || echo "No build artifacts found."

clean:             ## Clean all build artifacts and cache
	@$(MAKE) clean-pyc
	@$(MAKE) clean-venv
	@$(MAKE) clean-build-artifacts
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + || echo "No .pytest_cache directories found."

## ========== Helpers ==========

check-env:         ## Internal: check that .env file exists
	@if [ ! -f ".env" ]; then \
		echo "Error: .env file not found."; exit 1; \
	fi

# Define helper variables for environment activation
venv-activate = . .venv/bin/activate
load-env = set -a && . .env && set +a
venv-run = $(venv-activate) && $(load-env) &&

## ========== Install ==========

install-uv:        ## Install the uv package manager
	@$(venv-run) pip install uv

install-wfsm:      ## Install workflow service manager from AGNTCY
	curl -sSL https://raw.githubusercontent.com/agntcy/workflow-srv-mgr/refs/heads/install-sh-tag-cmd-args/install.sh -t v0.3.1 | bash

## ========== Build & Lint ==========

build:             ## Build the package using Poetry
	@poetry build

lint: setup-venv   ## Run ruff linter
	@echo "Running ruff linter..."
	@$(venv-activate) && poetry install && ruff check $(AGENT_NAME) tests

ruff-fix: setup-venv     ## Auto-fix lint errors
	@$(venv-activate) && ruff check $(AGENT_NAME) tests --fix

## ========== Run Targets ==========

## ========== Run the Agent Servers ==========
run:               ## Run the default agent
	@$(venv-run) python3 -m agent_template

run-acp:           ## Run ACP agent with wfsm
	@$(MAKE) check-env
	@$(venv-run) wfsm deploy -b ghcr.io/sriaradhyula/acp/wfsrv:latest -m ./$(AGENT_NAME)/protocol_bindings/acp_server/agent.json --envFilePath=./.env --dryRun=false

verify-a2a-sdk:    ## Verify A2A SDK is available
	@$(venv-run) python3 -c "import a2a; print('A2A SDK imported successfully')"

run-a2a:           ## Run A2A agent
	@$(MAKE) check-env
	@A2A_AGENT_PORT=$$(cat .env | grep A2A_AGENT_PORT | cut -d '=' -f2); \
	$(venv-run) uv run $(AGENT_NAME) --host 0.0.0.0 --port $${A2A_AGENT_PORT:-8000}

run-mcp:            ## Run MCP agent
	@$(MAKE) check-env
	@$(venv-run) set +a && source .env && set -a && MCP_MODE=SSE uv run $(AGENT_NAME)/protocol_bindings/mcp_server/mcp_argocd/server.py

## ========== Run the Agent Clients ==========

run-acp-client:    ## Run the ACP client
	@$(MAKE) check-env
	@$(venv-run) set +a && source .env && set -a && uv run client/acp_client.py

run-a2a-client:    ## Run the A2A client
	@$(MAKE) check-env
	@$(venv-run) set +a && source .env && set -a && uv run client/a2a_client.py

run-mcp-client:   ## Run the MCP client
	@$(MAKE) check-env
	@$(venv-run) set +a && source .env && set -a && uv run client/mcp_client.py

run-curl-client:   ## Run the curl-based test client
	@$(MAKE) check-env
	@$(venv-run) ./client/client_curl.sh

langgraph-dev:     ## Run the agent with LangGraph dev mode
	@$(venv-run) langgraph dev

evals:             ## Run agent evaluation script
	@$(venv-run) uv add agentevals tabulate pytest
	@$(venv-run) uv run evals/strict_match/test_strict_match.py

## ========== Docker ==========

## Build Docker image for ACP agent

build-docker-acp:  ## Build Docker image for ACP
	@echo "Building Docker image for ACP..."

	@docker build -t $(AGENT_NAME_DASH):acp-latest -f build/Dockerfile.acp .
	@echo "Docker image $(AGENT_NAME_DASH):acp-latest built successfully."

build-docker-acp-tag: build-docker-acp ## Tag the Docker image for ACP
	@echo "Tagging Docker image for ACP..."
	@docker tag $(AGENT_NAME_DASH):acp-latest ghcr.io/cnoe-io/$(AGENT_NAME_DASH):acp-latest;
	@echo "Docker image tagged as ghcr.io/cnoe-io/$(AGENT_NAME_DASH):acp-latest"

build-docker-acp-push: ## Push the tagged Docker image to registry
	@echo "Pushing Docker image to registry..."
	@docker push ghcr.io/cnoe-io/$(AGENT_NAME_DASH):acp-latest
	@echo "Docker image pushed successfully"

build-docker-acp-tag-and-push: build-docker-acp build-docker-acp-tag build-docker-acp-push ## Build, tag and push Docker image for ACP
	@echo "Build, tag, and push workflow completed successfully"

## Build Docker image for A2A agent
build-docker-a2a:  ## Build Docker image for A2A
	@echo "Building Docker image for A2A..."
	@docker build -t $(AGENT_NAME_DASH):a2a-latest -f build/Dockerfile.a2a .
	@echo "Docker image $(AGENT_NAME_DASH):a2a-latest built successfully."

build-docker-a2a-tag: build-docker-a2a ## Tag the Docker image for A2A
	@echo "Tagging Docker image for A2A..."
	@AGENT_NAME_DASH=$$(echo $(AGENT_NAME) | tr '_' '-');
	@docker tag $(AGENT_NAME_DASH):a2a-latest ghcr.io/cnoe-io/$(AGENT_NAME_DASH):a2a-latest
	@echo "Docker image tagged as ghcr.io/cnoe-io/$(AGENT_NAME_DASH):a2a-latest"

build-docker-a2a-push: ## Push the tagged Docker image to registry
	@echo "Pushing Docker image to registry..."
	@docker push ghcr.io/cnoe-io/$(AGENT_NAME_DASH):a2a-latest
	@echo "Docker image pushed successfully"

build-docker-a2a-tag-and-push: build-docker-a2a build-docker-a2a-tag build-docker-a2a-push ## Build, tag and push Docker image for A2A
	@echo "Build, tag, and push workflow completed successfully"

## ========= Run Docker ==========

# Run Docker container for ACP agent
run-docker-acp: ## Run the ACP agent in Docker
	# Set API_HOST to 0.0.0.0 to bind the workflow server to all network interfaces
	# This allows the agent to accept connections from any IP address, not just localhost

	@echo "Running Docker container for agent_argocd with agent ID: $$AGENT_ID"
	@AGENT_ID=$$(cat .env | grep CNOE_AGENT_ARGOCD_ID | cut -d '=' -f2) \
	ARGOCD_PORT=$$(cat .env | grep CNOE_AGENT_ARGOCD_PORT | cut -d '=' -f2) \
	ACP_AGENT_IMAGE=$$(cat .env | grep ACP_AGENT_IMAGE | cut -d '=' -f2) \
	LOCAL_AGENT_PORT=$${ARGOCD_PORT:-10000} \
	LOCAL_AGENT_IMAGE=$${ACP_AGENT_IMAGE:-ghcr.io/cnoe-io/agent-argocd:acp-latest}; \
	echo "========================================================================\n"; \
	echo "==                       ARGOCD AGENT DOCKER RUN                      ==\n"; \
	echo "==                Do not use uvicorn port in the logs                 ==\n"; \
	echo "========================================================================\n"; \
	echo "Using Agent Image: $$LOCAL_AGENT_IMAGE \n"; \
	echo "Using Agent ID: $$AGENT_ID \n"; \
	echo "Using Agent Port: localhost:$$LOCAL_AGENT_PORT \n"; \
	echo "========================================================================\n"; \
	docker run -p $$LOCAL_AGENT_PORT:8000 -it \
		-v $(PWD)/.env:/opt/agent_src/.env \
		--env-file .env \
		-e AGWS_STORAGE_PERSIST=False \
		-e AGENT_MANIFEST_PATH="manifest.json" \
		-e AGENTS_REF='{"'$$AGENT_ID'": "agent_argocd.graph:graph"}' \
		-e AGENT_ID=$$AGENT_ID \
		-e AIOHTTP_CLIENT_MAX_REDIRECTS=10 \
		-e AIOHTTP_CLIENT_TIMEOUT=60 \
		-e API_HOST=0.0.0.0 \
		$$LOCAL_AGENT_IMAGE

# Run Docker container for A2A agent

run-docker-a2a: ## Run the A2A agent in Docker
	LOCAL_A2A_AGENT_IMAGE=$${A2A_AGENT_IMAGE:-ghcr.io/cnoe-io/agent_argocd:a2a-latest}; \
	LOCAL_AGENT_PORT=8000; \
	echo "==================================================================="; \
	echo "                      A2A AGENT DOCKER RUN                         "; \
	echo "==================================================================="; \
	echo "Using Agent Image: $$LOCAL_AGENT_IMAGE"; \
	echo "Using Agent Port: $$LOCAL_AGENT_PORT"; \
	echo "==================================================================="; \
	docker run -p $$LOCAL_AGENT_PORT:$$LOCAL_AGENT_PORT -it \
		$$LOCAL_A2A_AGENT_IMAGE


## ========= Tests ==========
test: setup-venv build         ## Run all tests excluding evals
	@echo "Running unit tests..."
	@$(venv-activate) && poetry install
	@$(venv-activate) && poetry add pytest-asyncio --dev
	@$(venv-activate) && poetry add pytest-cov --dev
	@$(venv-activate) && pytest -v --tb=short --disable-warnings --maxfail=1 --ignore=evals --cov=$(AGENT_NAME) --cov-report=term --cov-report=xml

## ========= AGNTCY Agent Directory ==========
registry-agntcy-directory: ## Update the AGNTCY directory
	@echo "Registering $(AGENT_NAME) to AGNTCY Agent Directory..."
	@dirctl hub push outshift_platform_engineering/agent_argocd ./$(AGENT_NAME)/protocol_bindings/acp_server/agent.json

## ========== Licensing & Help ==========

add-copyright-license-headers: ## Add license headers with Google tool
	@docker run --rm -v $(shell pwd)/$(AGENT_NAME):/workspace ghcr.io/google/addlicense:latest -c "CNOE" -l apache -s=only -v /workspace

help:              ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-30s %s\n", $$1, $$2}'
