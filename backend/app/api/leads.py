import json

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, File, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import csv
import io

from app.database.connection import SessionLocal
from app.database.models import LeadDB
from app.models.lead import Lead
from app.agents.enrichment_agent import enrich_lead
from app.agents.competitor_agent import analyze_competitor_agent
from app.agents.outreach_agent import generate_outreach_agent


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _serialize_lead(lead: LeadDB) -> dict:
    return {
        "id": lead.id,
        "name": lead.name,
        "email": lead.email,
        "company": lead.company,
        "website": lead.website,
        "job_title": lead.job_title,
        "industry": lead.industry,
        "employee_count": lead.employee_count,
        "location": lead.location,
        "founded_year": lead.founded_year,
        "technologies": json.loads(lead.technologies or "[]"),
        "revenue_range": lead.revenue_range,
        "key_executives": json.loads(lead.key_executives or "[]") if lead.key_executives else [],
        "buying_signals": json.loads(lead.buying_signals or "[]"),
        "pain_points": json.loads(lead.pain_points or "[]"),
        "product_fit": lead.product_fit,
        "qualification_verdict": lead.qualification_verdict,
        "qualification_details": json.loads(lead.qualification_details or "{}"),
        "lead_score": lead.lead_score,
        "lead_priority": lead.lead_priority,
        "score_breakdown": json.loads(lead.score_breakdown or "{}"),
        "competitor": lead.competitor,
        "competitor_weakness": lead.competitor_weakness,
        "opportunity": lead.opportunity,
        "positioning": lead.positioning,
        "outreach_subject": lead.outreach_subject,
        "outreach_body": lead.outreach_body,
        "status": lead.status,
        "enriched_at": lead.enriched_at.isoformat() if lead.enriched_at else None,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
    }


@router.post("/leads")
def create_lead(lead: Lead, db: Session = Depends(get_db)):
    """Create a lead and run the full Phase 1 pipeline (Enrich → Signals → Qualify → Score)."""
    new_lead = LeadDB(
        name=lead.name,
        email=lead.email,
        company=lead.company,
        website=lead.website,
        job_title=lead.job_title,
        status="new"
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    enriched = enrich_lead(new_lead.id)

    if enriched:
        return {
            "message": "Lead created and fully processed",
            "lead": _serialize_lead(enriched)
        }

    return {
        "message": "Lead created (enrichment failed)",
        "lead": _serialize_lead(new_lead)
    }


@router.post("/leads/import")
async def import_leads(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import leads from a CSV file and enrich them synchronously."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    contents = await file.read()
    decoded = contents.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no headers")

    # Lowercase and strip all headers to make matching robust
    reader.fieldnames = [str(f).strip().lower() for f in reader.fieldnames]

    imported_count = 0
    imported_ids = []
    for row in reader:
        name = row.get("name") or row.get("full name") or row.get("first name") or row.get("lead name")
        email = row.get("email") or row.get("email address") or row.get("work email")
        company = row.get("company") or row.get("company name") or row.get("account")
        
        # If all essential fields are missing, try to get anything or just use fallback
        if not name and not email and not company:
            # Maybe it's a completely different format, skip empty rows
            if not any(row.values()):
                continue
            
        name = name or "Unknown Name"
        email = email or "unknown@example.com"
        company = company or "Unknown Company"
            
        website = row.get("website") or row.get("domain") or row.get("url")
        job_title = row.get("job title") or row.get("title") or row.get("role") or row.get("job_title")
        
        new_lead = LeadDB(
            name=name,
            email=email,
            company=company,
            website=website,
            job_title=job_title,
            status="new"
        )
        db.add(new_lead)
        db.flush() # flush to get the id without committing everything yet
        imported_ids.append(new_lead.id)
        imported_count += 1
        
    db.commit()

    # Process enrichment concurrently but wait for ALL to complete before responding
    from concurrent.futures import ThreadPoolExecutor, as_completed
    enriched_count = 0
    if imported_ids:
        def safe_enrich(lead_id):
            try:
                enrich_lead(lead_id)
                return True
            except Exception as e:
                print(f"[WARN] Enrichment failed for lead {lead_id}: {e}")
                return False

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(safe_enrich, imported_ids))
            enriched_count = sum(1 for r in results if r)

    return {
        "message": f"Imported {imported_count} leads, analyzed {enriched_count} successfully",
        "imported_count": imported_count,
        "enriched_count": enriched_count
    }


@router.get("/leads")
def get_leads(db: Session = Depends(get_db)):
    """List all leads (newest first)."""
    leads = db.query(LeadDB).order_by(LeadDB.created_at.desc()).all()
    return [_serialize_lead(l) for l in leads]


@router.get("/leads/stats")
def get_lead_stats(db: Session = Depends(get_db)):
    """Aggregate stats for the dashboard."""
    leads = db.query(LeadDB).all()
    total = len(leads)
    qualified = sum(1 for l in leads if l.qualification_verdict in ("HIGH", "MEDIUM"))
    hot = sum(1 for l in leads if l.lead_priority == "HOT")
    warm = sum(1 for l in leads if l.lead_priority == "WARM")
    cold = sum(1 for l in leads if l.lead_priority == "COLD")
    avg_score = (
        sum(l.lead_score for l in leads if l.lead_score) / max(len([l for l in leads if l.lead_score]), 1)
    )
    return {
        "total_leads": total,
        "qualified": qualified,
        "hot_leads": hot,
        "warm_leads": warm,
        "cold_leads": cold,
        "average_score": round(avg_score, 1)
    }


@router.get("/leads/{lead_id}")
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Get full detail for a single lead."""
    lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return _serialize_lead(lead)


@router.post("/leads/{lead_id}/competitor-analysis")
def run_competitor_analysis(lead_id: int, db: Session = Depends(get_db)):
    """Phase 2: Run competitor analysis for a lead."""
    lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    updated = analyze_competitor_agent(lead_id)
    if not updated:
        raise HTTPException(status_code=500, detail="Competitor analysis failed")

    return {
        "message": "Competitor analysis complete",
        "lead": _serialize_lead(updated)
    }


@router.post("/leads/{lead_id}/outreach")
def run_outreach_generation(lead_id: int, db: Session = Depends(get_db)):
    """Phase 2: Generate personalized outreach for a lead."""
    lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    updated = generate_outreach_agent(lead_id)
    if not updated:
        raise HTTPException(status_code=500, detail="Outreach generation failed")

    return {
        "message": "Outreach generated",
        "subject": updated.outreach_subject,
        "body": updated.outreach_body
    }