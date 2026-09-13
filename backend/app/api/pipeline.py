from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import PipelineDB, LeadDB
from app.agents.pipeline_agent import process_pipeline_entry
from app.services.pipeline_service import compute_forecast


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PipelineCreate(BaseModel):
    lead_id: int
    deal_stage: str          # prospecting/qualification/proposal/negotiation/closed_won/closed_lost
    deal_value: float
    close_date: Optional[str] = None
    probability: Optional[float] = None
    sales_activity_score: Optional[int] = 0
    meeting_count: Optional[int] = 0
    email_engagement: Optional[int] = 0
    days_in_stage: Optional[int] = 0
    notes: Optional[str] = None


def _serialize_pipeline(p: PipelineDB, lead: LeadDB = None) -> dict:
    return {
        "id": p.id,
        "lead_id": p.lead_id,
        "lead_name": lead.name if lead else None,
        "company": lead.company if lead else None,
        "deal_stage": p.deal_stage,
        "deal_value": p.deal_value,
        "close_date": p.close_date,
        "probability": p.probability,
        "expected_revenue": p.expected_revenue,
        "sales_activity_score": p.sales_activity_score,
        "meeting_count": p.meeting_count,
        "email_engagement": p.email_engagement,
        "days_in_stage": p.days_in_stage,
        "at_risk": p.at_risk,
        "risk_reason": p.risk_reason,
        "notes": p.notes,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


@router.post("/pipeline")
def create_pipeline_entry(data: PipelineCreate, db: Session = Depends(get_db)):
    """Add a deal to the pipeline and run risk + revenue calculations."""
    lead = db.query(LeadDB).filter(LeadDB.id == data.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    entry = PipelineDB(
        lead_id=data.lead_id,
        deal_stage=data.deal_stage,
        deal_value=data.deal_value,
        close_date=data.close_date,
        probability=data.probability,
        sales_activity_score=data.sales_activity_score,
        meeting_count=data.meeting_count,
        email_engagement=data.email_engagement,
        days_in_stage=data.days_in_stage,
        notes=data.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Run pipeline agent for risk + revenue calc
    processed = process_pipeline_entry(entry.id)
    final = processed if processed else entry

    return {
        "message": "Pipeline entry created",
        "pipeline": _serialize_pipeline(final, lead)
    }


@router.get("/pipeline")
def get_pipeline(db: Session = Depends(get_db)):
    """List all pipeline deals."""
    entries = db.query(PipelineDB).order_by(PipelineDB.deal_value.desc()).all()
    result = []
    for entry in entries:
        lead = db.query(LeadDB).filter(LeadDB.id == entry.lead_id).first()
        result.append(_serialize_pipeline(entry, lead))
    return result


@router.get("/pipeline/forecast")
def get_forecast(db: Session = Depends(get_db)):
    """Aggregate pipeline forecast + at-risk deals."""
    entries = db.query(PipelineDB).all()
    if not entries:
        return {
            "total_pipeline": 0,
            "expected_revenue": 0,
            "best_case": 0,
            "at_risk_deals": [],
            "deal_count": 0
        }

    entry_dicts = []
    for e in entries:
        lead = db.query(LeadDB).filter(LeadDB.id == e.lead_id).first()
        entry_dicts.append({
            "lead_id": e.lead_id,
            "lead_name": lead.name if lead else None,
            "company": lead.company if lead else None,
            "deal_stage": e.deal_stage,
            "deal_value": e.deal_value,
            "probability": e.probability,
            "at_risk": e.at_risk,
            "risk_reason": e.risk_reason,
        })

    forecast = compute_forecast(entry_dicts)
    forecast["deal_count"] = len(entries)
    return forecast


@router.post("/pipeline/seed")
def seed_pipeline(db: Session = Depends(get_db)):
    """Seed 5 sample pipeline entries for demo purposes."""
    # Get up to 5 leads
    leads = db.query(LeadDB).limit(5).all()
    if not leads:
        raise HTTPException(status_code=400, detail="No leads found. Create some leads first.")

    sample_stages = [
        {"stage": "negotiation", "value": 250000, "prob": 0.70, "days": 12, "meetings": 4, "emails": 8},
        {"stage": "proposal",    "value": 180000, "prob": 0.40, "days": 8,  "meetings": 2, "emails": 5},
        {"stage": "proposal",    "value": 120000, "prob": 0.40, "days": 35, "meetings": 0, "emails": 1},
        {"stage": "qualification","value": 300000, "prob": 0.20, "days": 50, "meetings": 0, "emails": 0},
        {"stage": "negotiation", "value": 150000, "prob": 0.70, "days": 20, "meetings": 3, "emails": 6},
    ]

    created = []
    for i, lead in enumerate(leads):
        # Skip if pipeline entry already exists
        existing = db.query(PipelineDB).filter(PipelineDB.lead_id == lead.id).first()
        if existing:
            continue

        s = sample_stages[i % len(sample_stages)]
        entry = PipelineDB(
            lead_id=lead.id,
            deal_stage=s["stage"],
            deal_value=s["value"],
            probability=s["prob"],
            days_in_stage=s["days"],
            meeting_count=s["meetings"],
            email_engagement=s["emails"],
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        process_pipeline_entry(entry.id)
        created.append(entry.id)

    return {"message": f"Seeded {len(created)} pipeline entries", "ids": created}
