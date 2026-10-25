# Coverly Shelf landing: https://coverly-shelf.maecly.com
# Standard library only: python3 and node, no install step.

SHELL := /bin/bash
.DEFAULT_GOAL := help

SITE_OUT := target/site
SITE_PORT ?= 8080
# Where `make sync-tokens` reads the Coverly family design tokens.
TOKENS_URL ?= https://raw.githubusercontent.com/MAECLY/coverly-roms/main/design/tokens.json

.PHONY: help
help: ## List the targets.
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

.PHONY: site
site: build ## Build, then serve the landing on http://localhost:SITE_PORT (default 8080).
	@echo "Serving $(SITE_OUT) on http://localhost:$(SITE_PORT) (Ctrl+C to stop)"
	python3 -m http.server $(SITE_PORT) --bind 127.0.0.1 -d "$(SITE_OUT)"

.PHONY: build
build: ## Build target/site exactly as Vercel does.
	bash scripts/site/vercel_build.sh

.PHONY: check
check: ## Every gate: tokens and contrast, files, links, ES/EN parity, head/CSP, budgets, metrics, metrics tests.
	node scripts/brand/build_tokens.mjs --check
	python3 -I scripts/site/check_site.py
	node --test scripts/site/*.test.mjs

.PHONY: icons
icons: ## Rasterise the icons from design/icon (needs Chrome or Chromium).
	node scripts/site/icons.mjs

.PHONY: og
og: ## Render the Open Graph cards site/assets/og.png and og-en.png (needs Chrome or Chromium).
	node scripts/site/og.mjs

.PHONY: tokens
tokens: ## Regenerate site/assets/tokens.css from design/tokens.json.
	node scripts/brand/build_tokens.mjs

.PHONY: sync-tokens
sync-tokens: ## Fetch the family design/tokens.json from MAECLY/coverly-roms (main), then regenerate.
	@tmp="$$(mktemp)"; trap 'rm -f "$$tmp"' EXIT; \
	  curl -fsSL "$(TOKENS_URL)" -o "$$tmp" && \
	  python3 -I -c 'import json, sys; json.load(open(sys.argv[1]))' "$$tmp" && \
	  if cmp -s "$$tmp" design/tokens.json; then \
	    echo "design/tokens.json already matches"; \
	  else \
	    cp "$$tmp" design/tokens.json && echo "updated design/tokens.json"; \
	  fi
	$(MAKE) --no-print-directory tokens
