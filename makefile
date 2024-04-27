.PHONY: init frontend run-consumer all clean test


init:
	poetry install
	pre-commit install

frontend:
	poetry run streamlit run yem/frontend/main.py

run-consumer:
	python yem/consumer.py
