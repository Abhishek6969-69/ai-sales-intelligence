import json

from app.services.llm_service import qualify_lead
from app.database.models import LeadDB
from app.database.connection import SessionLocal


def qualify_lead_agent(lead_id: int) -> LeadDB | None:
    db = SessionLocal()
    try:
        lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
        if not lead:
            return None

        enrichment = {
            "industry": lead.industry,
            "employee_count": lead.employee_count,
            "location": lead.location,
            "technologies": json.loads(lead.technologies or "[]"),
            "revenue_range": lead.revenue_range,
        }

        signals = {
            "buying_signals": json.loads(lead.buying_signals or "[]"),
            "product_fit": lead.product_fit,
        }

        result = qualify_lead(enrichment=enrichment, signals=signals)

        lead.qualification_verdict = result.get("verdict")
        lead.qualification_details = json.dumps(result)
        db.commit()
        db.refresh(lead)

        return lead
    finally:
        db.close()
