"""
Production-ready FastAPI template.

Exposes a health endpoint that attempts a real connection to the configured
PostgreSQL host and reports the result. No tables/models are required --
the point is to prove the API, config, and database are wired together
correctly end-to-end (API -> Nginx -> Docker network -> Postgres).
"""

import logging

import psycopg2
from fastapi import FastAPI

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)


def check_database() -> dict:
    """Attempt a lightweight connection to Postgres and report status."""
    try:
        conn = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            connect_timeout=3,
        )
        conn.close()
        return {"connected": True, "host": settings.db_host, "detail": "ok"}
    except Exception as exc:  # noqa: BLE001 - we want to report any failure
        logger.warning("Database connection failed: %s", exc)
        return {"connected": False, "host": settings.db_host, "detail": str(exc)}


@app.get("/")
def root() -> dict:
    return {"service": settings.app_name, "environment": settings.environment}


@app.get("/health")
def health() -> dict:
    """
    Primary health check.

    Returns overall API status plus the live result of a database
    connection attempt -- this is what Nginx proxies to and what you
    should hit at http://localhost/health once docker compose is up.
    """
    db_status = check_database()
    return {
        "status": "ok",
        "api": "up",
        "database": db_status,
    }
