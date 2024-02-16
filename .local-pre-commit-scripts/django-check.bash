#!/usr/bin/env bash

if command -v poetry >/dev/null 2>&1; then
  POETRY_LOCATION=poetry
else
  POETRY_LOCATION=$POETRY_HOME/bin/poetry
fi

$POETRY_LOCATION run python manage.py check
