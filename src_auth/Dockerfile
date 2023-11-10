#########################################################
# Base Image
#########################################################

FROM python:3.10-slim-bullseye as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEDAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1.12 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup"

# prepend poetry to path
ENV PATH="$POETRY_HOME/bin:$PATH"

#########################################################
# Builder Image
#########################################################
FROM python-base as builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential

# Install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

# copy project requirenent files here to ensure they will be cached.

WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

#install runtine deps
RUN poetry config virtualenvs.in-project false && \
    poetry config virtualenvs.create false

RUN poetry install --no-dev


COPY ./src_auth ./src_auth

EXPOSE 24004

CMD ["uvicorn", "src_auth.app.service:app", "--host", "0.0.0.0", "--port", "24004"]
# CMD ["python", "-m", "src.app.service"]