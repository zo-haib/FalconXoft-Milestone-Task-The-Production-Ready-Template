# Production-Ready Template

A minimal, professionally structured backend template: **FastAPI + Poetry +
PostgreSQL + Nginx**, fully containerized with Docker Compose.

## Stack

| Layer         | Tool                          |
|---------------|--------------------------------|
| Dependency mgmt | [Poetry](https://python-poetry.org/) |
| API           | FastAPI + Uvicorn              |
| Database      | PostgreSQL 16 (persistent volume) |
| Reverse proxy | Nginx                          |
| Config/secrets| `.env` via `python-dotenv` / `pydantic-settings` |
| Container     | Multi-stage Dockerfile (slim runtime image) |

## Project structure

```
.
├── app/
│   ├── __init__.py
│   ├── config.py        # Settings loaded from .env (pydantic-settings)
│   └── main.py           # FastAPI app + /health DB check
├── nginx/
│   └── default.conf      # Reverse proxy -> api:8000
├── Dockerfile             # Multi-stage build (builder -> slim runtime)
├── docker-compose.yml     # api + db + nginx, one command
├── pyproject.toml / poetry.lock
├── .env.example           # Template for local secrets (commit this)
├── .env                    # Your real local secrets (NEVER commit this)
└── .gitignore
```

## Quickstart

```bash
git clone <this-repo>
cd production-ready-template
cp .env.example .env      # adjust values if you want, defaults work out of the box
docker compose up -d --build
```

Then open:

- **http://localhost/** — basic service info, proxied through Nginx
- **http://localhost/health** — confirms the API is up *and* that it can
  reach the Postgres container:

```json
{
  "status": "ok",
  "api": "up",
  "database": {
    "connected": true,
    "host": "db",
    "detail": "ok"
  }
}
```

Traffic flow: `you -> localhost:80 (nginx) -> api:8000 (fastapi) -> db:5432 (postgres)`,
all over the internal `backend` Docker network. Only Nginx's port 80 is
published to the host — the API and database are not directly reachable
from outside the Docker network.

## Local development (without Docker)

```bash
poetry install
poetry run uvicorn app.main:app --reload
```

Note: outside Docker, `DB_HOST=db` won't resolve (there's no `db` hostname
on your machine) — that's expected. Point `DB_HOST` in `.env` at a local
or reachable Postgres instance, or just run everything through
`docker compose up -d` where the `db` service name resolves automatically.

## Secrets

All configuration lives in `.env` (see `.env.example` for the full list:
app name, environment, secret key, DB host/port/name/user/password).
`.env` is listed in `.gitignore` and is never committed — `.env.example`
is the safe, checked-in template with placeholder values.

## Data persistence

Postgres data is stored in the named volume `pgdata`, so `docker compose
down` (without `-v`) and `docker compose up -d` again will preserve your
data. Use `docker compose down -v` to wipe it.

## Useful commands

```bash
docker compose up -d --build   # build and start everything
docker compose logs -f api     # tail API logs
docker compose ps              # see service status/health
docker compose down            # stop (keeps volume/data)
docker compose down -v         # stop and wipe the database volume
```
