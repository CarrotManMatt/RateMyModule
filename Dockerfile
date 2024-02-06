FROM python:3.12 as builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=true \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apt-get update && apt-get install --no-install-recommends -y curl build-essential

RUN pip install poetry

WORKDIR /app

COPY poetry.lock pyproject.toml README.md ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root --no-interaction --with deploy

FROM python:3.12-slim as runtime

ENV LANG=C.UTF-8

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY . ./

ENTRYPOINT ["gunicorn", "core.wsgi:APPLICATION", "--bind=0.0.0.0:8000"]
