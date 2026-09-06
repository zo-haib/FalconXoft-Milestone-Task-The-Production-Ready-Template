# syntax=docker/dockerfile:1

# ---------- Stage 1: builder ----------
# Installs Poetry and resolves dependencies into a self-contained venv.
FROM python:3.12-slim AS builder

ENV POETRY_VERSION=2.4.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

# Copy only dependency manifests first to maximize layer caching.
COPY pyproject.toml poetry.lock ./

# Install only runtime dependencies (no dev deps, no root package) into .venv
RUN poetry install --no-root --only main --no-ansi

# ---------- Stage 2: runtime ----------
# Minimal final image: no compilers, no Poetry, just Python + the venv + app code.
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# libpq5 is the runtime (non-dev) Postgres client library needed by psycopg2-binary
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 appuser

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY app ./app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
