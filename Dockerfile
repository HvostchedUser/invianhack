FROM python:3.11

WORKDIR /code

ARG YOUR_ENV

ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.6.1 \
  PYTHONPATH="${PYTHONPATH}:/code"

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY poetry.lock pyproject.toml makefile /code/

RUN poetry install --only=main --no-interaction --no-ansi

COPY static /code/static
COPY ./yem /code/yem
