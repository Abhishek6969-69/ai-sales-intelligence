import json

from app.services.llm_service import generate_outreach
from app.database.models import LeadDB
from app.database.connection import SessionLocal


def generate_outreach_agent(lead_id: int) -> LeadDB | None:
    db = SessionLocal()
    try:
        lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
        if not lead:
            return None

        lead_data = {
            "name": lead.name,
            "job_title": lead.job_title,
            "company": lead.company,
            "industry": lead.industry,
            "buying_signals": json.loads(lead.buying_signals or "[]"),
            "pain_points": json.loads(lead.pain_points or "[]"),
            "competitor": lead.competitor,
            "positioning": lead.positioning,
        }

        result = generate_outreach(lead_data=lead_data)

        lead.outreach_subject = result.get("subject")
        lead.outreach_body = result.get("body")
        db.commit()
        db.refresh(lead)

        return lead
    finally:
        db.close()
