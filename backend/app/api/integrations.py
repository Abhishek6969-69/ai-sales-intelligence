import os

from fastapi import APIRouter
from sqlalchemy import text

from app.database.connection import engine


router = APIRouter()


def _database_status() -> str:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return "connected"
    except Exception:
        return "error"


@router.get("/integrations/status")
def get_integration_status():
    """Return safe connection metadata without exposing provider credentials."""
    return {
        "integrations": [
            {
                "id": "groq",
                "name": "Groq",
                "category": "AI reasoning",
                "description": "Qualification, competitor analysis, outreach, and forecast narrative generation.",
                "status": "connected" if os.getenv("GROQ_API_KEY") else "needs_setup",
                "managed_by": "backend/.env",
            },
            {
                "id": "tinyfish",
                "name": "TinyFish",
                "category": "Web research",
                "description": "Company enrichment, buying-signal research, and competitor discovery.",
                "status": "connected" if os.getenv("TINYFISH_API_KEY") else "needs_setup",
                "managed_by": "backend/.env",
            },
            {
                "id": "postgresql",
                "name": "PostgreSQL",
                "category": "System of record",
                "description": "Stores leads, enrichment, pipeline deals, scores, and forecast state.",
                "status": _database_status(),
                "managed_by": "DATABASE_URL",
            },
            {
                "id": "crm",
                "name": "CRM sync",
                "category": "Revenue operations",
                "description": "Push qualified leads and pipeline updates into an external CRM.",
                "status": "available_next",
                "managed_by": "OAuth connection",
            },
        ]
    }
