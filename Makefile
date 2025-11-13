################################################################################################
# Configurable variables
PYTHON_MIN_VERSION := 3.11
LEADERBOARD_NAMES := zrc_prosaudit

################################################################################################
# FILES
JS_FILES := $(addprefix static/js/, $(addsuffix .js, $(LEADERBOARD_NAMES)))
PREVIEW_FILES := $(addprefix static/preview/, $(addsuffix .html, $(LEADERBOARD_NAMES)))
SNIPPET_FILES := $(addprefix static/snippets/, $(addsuffix .html, $(LEADERBOARD_NAMES)))
STAMPS := $(addprefix .stamps/, $(addsuffix .stamp, $(LEADERBOARD_NAMES)))
# LOCATIONS
VENV_DIR := .venv
REQUIREMENTS := requirements.txt
# Colors
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color


# Detect if uv is available
UV_EXISTS := $(shell command -v uv 2> /dev/null)

# Detect if .venv exists
VENV_EXISTS := $(wildcard $(VENV_DIR)/bin/python)

# Determine the command prefix based on environment
ifdef UV_EXISTS
    RUN_PREFIX := uv run
    ENV_TYPE := uv
else ifdef VENV_EXISTS
    RUN_PREFIX := $(VENV_DIR)/bin/python -m
    ENV_TYPE := venv
else
    RUN_PREFIX := @echo "$(RED)Error: No environment found. Run 'make install-requirements' first$(NC)" && exit 1 &&
    ENV_TYPE := none
endif

# Default target
.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help message
	@echo "$(GREEN)CoML Leaderboard Builder$(NC)"
	@echo "$(YELLOW)Current environment: $(ENV_TYPE)$(NC)"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "Environment detection:"
	@if [ -n "$(UV_EXISTS)" ]; then \
		echo "  ✓ uv found at: $(UV_EXISTS)"; \
	else \
		echo "  ✗ uv not found"; \
	fi
	@if [ -n "$(VENV_EXISTS)" ]; then \
		echo "  ✓ .venv found"; \
	else \
		echo "  ✗ .venv not found"; \
	fi


.PHONY: install-requirements
install-requirements: ## Install requirements (auto-detects uv or creates .venv)
	@echo "$(YELLOW)Setting up environment...$(NC)"
	@if [ -n "$(UV_EXISTS)" ]; then \
		echo "$(GREEN)✓ uv detected - skipping setup (uv run will handle it)$(NC)"; \
	else \
		echo "$(YELLOW)uv not found, checking Python version...$(NC)"; \
		if command -v python3 >/dev/null 2>&1; then \
			PYTHON_VERSION=$$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'); \
			PYTHON_MAJOR=$$(echo $$PYTHON_VERSION | cut -d. -f1); \
			PYTHON_MINOR=$$(echo $$PYTHON_VERSION | cut -d. -f2); \
			if [ "$$PYTHON_MAJOR" -ge 3 ] && [ "$$PYTHON_MINOR" -ge 10 ]; then \
				echo "$(GREEN)✓ Python $$PYTHON_VERSION found$(NC)"; \
				if [ ! -d "$(VENV_DIR)" ]; then \
					echo "$(YELLOW)Creating virtual environment...$(NC)"; \
					python3 -m venv $(VENV_DIR); \
					echo "$(GREEN)✓ Virtual environment created$(NC)"; \
				else \
					echo "$(GREEN)✓ Virtual environment already exists$(NC)"; \
				fi; \
				echo "$(YELLOW)Installing requirements...$(NC)"; \
				$(VENV_DIR)/bin/pip install --quiet --upgrade pip; \
				if [ -f "$(REQUIREMENTS)" ]; then \
					$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS); \
					echo "$(GREEN)✓ Requirements installed$(NC)"; \
				else \
					echo "$(RED)✗ $(REQUIREMENTS) not found$(NC)"; \
					echo "$(YELLOW)Installing mkdocs and common plugins...$(NC)"; \
					$(VENV_DIR)/bin/pip install mkdocs mkdocs-material pymdown-extensions; \
					echo "$(GREEN)✓ Basic MkDocs setup installed$(NC)"; \
				fi; \
			else \
				echo "$(RED)✗ Python version $$PYTHON_VERSION is below minimum required $(PYTHON_MIN_VERSION)$(NC)"; \
				exit 1; \
			fi; \
		else \
			echo "$(RED)✗ Python3 not found. Please install Python $(PYTHON_MIN_VERSION) or higher$(NC)"; \
			exit 1; \
		fi; \
	fi


.PHONY: requirements-freeze
requirements-freeze: ## Freeze current requirements
	@if [ "$(ENV_TYPE)" = "venv" ]; then \
		echo "$(YELLOW)Freezing requirements...$(NC)"; \
		$(VENV_DIR)/bin/pip freeze > requirements-frozen.txt; \
		echo "$(GREEN)✓ Requirements frozen to requirements-frozen.txt$(NC)"; \
	elif [ "$(ENV_TYPE)" = "uv" ]; then \
		echo "$(YELLOW)Freezing requirements with uv...$(NC)"; \
		uv pip freeze > requirements-frozen.txt; \
		echo "$(GREEN)✓ Requirements frozen to requirements-frozen.txt$(NC)"; \
	else \
		echo "$(RED)Error: No environment found$(NC)"; \
		exit 1; \
	fi


.PHONY: preview
preview: ## Serve development site (includes draft pages)
	@echo "$(YELLOW)Starting development server with draft pages...$(NC)"
	@if [ "$(ENV_TYPE)" = "none" ]; then \
		echo "$(RED)Error: No environment found. Run 'make install-requirements' first$(NC)"; \
		exit 1; \
	fi
	@$(RUN_PREFIX) -m http.server -b localhost -d static/ 9599
	

.PHONY: build-all
build-all: $(JS_FILES) $(PREVIEW_FILES) $(SNIPPET_FILES) ## Build all leaderboards	


.PHONY: $(LEADERBOARD_NAMES)
$(LEADERBOARD_NAMES):  ## Named leaderboards
	@$(MAKE) static/js/$@.js static/preview/$@.html static/snippet/$@.html


static/js/%.js: .stamps/%.stamp
	@:

static/preview/%.html: .stamps/%.stamp
	@:

static/snippet/%.html: .stamps/%.stamp
	@:


.stamps/%.stamp: | .stamps
	uv run python -m leaderboard_builder make-html --name $*
	@touch $@

.stamps:
	@mkdir -p .stamps


.PHONY: clean
clean:
	rm -f $(JS_FILES)
	rm -f $(PREVIEW_FILES)
	rm -f $(SNIPPET_FILES)