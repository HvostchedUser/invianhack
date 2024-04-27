.PHONY: init frontend all clean test


init:
	poetry install
	pre-commit install

frontend:
	poetry run streamlit run yem/frontend/main.py --server.runOnSave true
