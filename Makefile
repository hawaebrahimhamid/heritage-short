.PHONY: help setup validate test smoke-test flux-test generate-prompts run-pipeline clean

SHELL := bash
PYTHON := python
STORYBOARD := storyboard.json
SCHEMA := schema/storyboard.schema.json

help:
	@echo "Heritage Short Film Production Pipeline"
	@echo "----------------------------------------"
	@echo "Available commands:"
	@echo "  make setup            Install required dependencies"
	@echo "  make validate         Validate storyboard.json against JSON schema"
	@echo "  make smoke-test       Run Gemini and environment connectivity smoke test"
	@echo "  make flux-test        Run single-call Cloudflare Workers AI FLUX test"
	@echo "  make generate-prompts Compile prompt deck for text-to-video / audio"
	@echo "  make run-pipeline     Execute the full generative media pipeline"
	@echo "  make test             Run test suite across pipeline modules"
	@echo "  make clean            Clean temporary render files in outputs/"

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt || echo "No requirements.txt found yet."

validate:
	$(PYTHON) pipeline/validate_storyboard.py --storyboard $(STORYBOARD) --schema $(SCHEMA)

smoke-test:
	$(PYTHON) pipeline/smoke_test.py

flux-test:
	$(PYTHON) pipeline/test_flux.py

generate-prompts:
	$(PYTHON) pipeline/prompt_compiler.py --input $(STORYBOARD) --output outputs/prompts.json

run-pipeline: validate
	$(PYTHON) pipeline/runner.py --storyboard $(STORYBOARD) --output-dir outputs/

test:
	$(PYTHON) -m unittest discover -s tests -p "*_test.py"

clean:
	rm -rf outputs/temp/* outputs/*.tmp
