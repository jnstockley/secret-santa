#!/usr/bin/env bash

export PYTHONPATH=src/:$PYTHONPATH
export INTERACTIVE_MODE=false
export DRY_RUN=true
export FILE_PATH=tests/secret_santa.csv

# Run Tests
uv run pytest --cov src --cov-branch --cov-report=xml --junitxml=junit.xml -o junit_family=legacy
