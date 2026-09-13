from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.models import Base
from app.database.connection import engine
from app.api.leads import router as leads_router
from app.api.pipeline import router as pipeline_router
from app.api.integrations import router as integrations_router

# Auto-create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Sales Intelligence Platform",
    version="3.0.0",
    description="Multi-agent AI platform for lead enrichment, qualification, scoring, and revenue forecasting"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads_router, tags=["Leads"])
app.include_router(pipeline_router, tags=["Pipeline"])
app.include_router(integrations_router, tags=["Integrations"])


@app.get("/")
def home():
    return {
        "message": "AI Sales Intelligence Platform API",
        "version": "3.0.0",
        "phases": ["Phase 1: Enrich + Qualify + Score", "Phase 2: Competitor + Outreach", "Phase 3: Pipeline Forecasting"],
        "docs": "/docs"
    }
