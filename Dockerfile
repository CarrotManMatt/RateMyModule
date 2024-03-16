FROM python:3.12 as builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_VIRTUALENVS_OPTIONS_ALWAYS_COPY=true \
    POETRY_VIRTUALENVS_OPTIONS_NO_PIP=true \
    POETRY_HOME=/opt/poetry

RUN apt-get update && apt-get install --no-install-recommends -y curl build-essential
RUN python3 -m venv $POETRY_HOME
RUN $POETRY_HOME/bin/pip install poetry==1.8.1

WORKDIR /app

COPY poetry.lock pyproject.toml README.adoc ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR $POETRY_HOME/bin/poetry install --without dev --no-root --no-interaction --with deploy

FROM python:3.12-slim as runtime

ENV LANG=C.UTF-8 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
RUN printf '#!/bin/sh\n\n./manage.py migrate --no-input\n./manage.py collectstatic --no-input\ngunicorn core.wsgi:APPLICATION --bind=0.0.0.0:8000\n' > /app/entrypoint.sh
WORKDIR /

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
WORKDIR /app
COPY LICENSE .en[v] core.d[b] core.sqlit[e] sqlite3.d[b] manage.py ./
RUN chmod +x manage.py

COPY core/ ./core/
COPY api_htmx/ ./api_htmx/
COPY api_rest/ ./api_rest/
COPY ratemymodule/ ./ratemymodule/
COPY web/ ./web/
COPY override-templates/ ./override-templates/

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
