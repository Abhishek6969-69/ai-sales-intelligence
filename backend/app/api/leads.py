from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import LeadDB
from app.models.lead import Lead
from app.agents.enrichment_agent import enrich_lead


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/leads")
def create_lead(lead: Lead, db: Session = Depends(get_db)):
    new_lead = LeadDB(
        name=lead.name,
        email=lead.email,
        company=lead.company,
        website=lead.website,
        job_title=lead.job_title
    )

    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    enriched_lead = enrich_lead(new_lead.id)

    if enriched_lead:
        return {
            "message": "Lead created and enriched successfully",
            "lead": {
                "id": enriched_lead.id,
                "name": enriched_lead.name,
                "email": enriched_lead.email,
                "company": enriched_lead.company,
                "website": enriched_lead.website,
                "job_title": enriched_lead.job_title,
                "industry": enriched_lead.industry,
                "employee_count": enriched_lead.employee_count,
                "location": enriched_lead.location,
                "founded_year": enriched_lead.founded_year,
                "technologies": enriched_lead.technologies,
                "revenue_range": enriched_lead.revenue_range
            }
        }

    return {
        "message": "Lead created successfully",
        "lead": {
            "id": new_lead.id,
            "name": new_lead.name,
            "email": new_lead.email,
            "company": new_lead.company,
            "website": new_lead.website,
            "job_title": new_lead.job_title
        }
    }


@router.get("/leads")
def get_leads(db: Session = Depends(get_db)):
    return db.query(LeadDB).all()