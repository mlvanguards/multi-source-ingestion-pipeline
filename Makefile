PYTHON := python3
PROJECT := multi-source-ingestion


install:
	poetry install

shell:
	poetry shell

run:
	poetry run python src/main.py
