.PHONY: help setup validate test smoke-test flux-test narration generate-stills generate-prompts run-pipeline clean

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
	@echo "  make narration        Generate Amharic voiceover narration & radio cut audio"
	@echo "  make generate-stills  Generate still images for Shots 1-7 with FLUX (seed 42)"
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

narration:
	$(PYTHON) pipeline/generate_narration.py

generate-stills:
	$(PYTHON) pipeline/generate_shot_stills.py

generate-prompts:
	$(PYTHON) pipeline/prompt_compiler.py --input $(STORYBOARD) --output outputs/prompts.json

run-pipeline: validate
	$(PYTHON) pipeline/runner.py --storyboard $(STORYBOARD) --output-dir outputs/

test:
	$(PYTHON) -m unittest discover -s tests -p "*_test.py"

clean:
	rm -rf outputs/temp/* outputs/*.tmp
