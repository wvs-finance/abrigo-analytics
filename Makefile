.PHONY: help venv install data data-raw data-onchain panels notebooks lint test verify clean publish publish-dry

PY := .venv/bin/python
UV := uv

help:
	@echo "Abrigo Analytics — common targets"
	@echo ""
	@echo "  make venv         Create .venv via uv (Python 3.13)"
	@echo "  make install      uv sync (or uv pip install -r requirements.txt)"
	@echo ""
	@echo "Data tiers (pick one — or run all sequentially for full reproducibility):"
	@echo "  make data         Tier 1: pull processed panels from HuggingFace (~30 sec, ~1 MB)"
	@echo "  make data-raw     Tier 2: re-download DANE GEIH zips + Banrep TRM (~30 min, ~5.3 GB)"
	@echo "  make data-onchain Tier 2: pull on-chain panels (Carbon basket, Mento-native) (~10 min)"
	@echo "  make panels       Tier 3: re-derive processed panels from Tier 2 raw (~1 hr)"
	@echo ""
	@echo "Analysis:"
	@echo "  make notebooks    Execute all notebook trios headless (nbconvert --execute)"
	@echo "  make verify       Hash-check Tier 3 outputs against published Tier 1"
	@echo ""
	@echo "Quality:"
	@echo "  make lint         ruff check on scripts/"
	@echo "  make test         pytest tests/"
	@echo "  make clean        Remove .venv, __pycache__, data/raw/"

venv:
	$(UV) venv --python 3.13

install:
	$(UV) pip install -r requirements.txt

# --- Data tiers -------------------------------------------------------------

data:
	$(PY) scripts/fetch_data.py --tier 1

data-raw:
	$(PY) scripts/fetch_geih.py
	$(PY) scripts/fetch_banrep.py

data-onchain:
	$(PY) scripts/fetch_onchain.py

panels:
	$(PY) scripts/build_panels.py

verify:
	$(PY) scripts/build_panels.py --verify-against-tier1

# --- HuggingFace publishing (maintainer-only) -------------------------------

publish-dry:
	$(PY) scripts/publish_to_hf.py --dry-run

publish:
	$(PY) scripts/publish_to_hf.py

# --- Analysis ---------------------------------------------------------------

notebooks:
	@for nb in $$(find notebooks simulations/notebooks -name '*.ipynb' -not -path '*/_nbconvert_template/*' -not -path '*/.ipynb_checkpoints/*'); do \
	  echo "Executing $$nb"; \
	  $(PY) -m jupyter nbconvert --to notebook --execute --inplace "$$nb" || exit 1; \
	done

# --- Quality ----------------------------------------------------------------

lint:
	$(PY) -m ruff check scripts/

test:
	$(PY) -m pytest

clean:
	rm -rf .venv __pycache__ .pytest_cache .ruff_cache
	rm -rf data/raw data/downloads data/probes data/extracted
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
