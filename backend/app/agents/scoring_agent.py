import json

from app.services.scoring_engine import calculate_score
from app.database.models import LeadDB
from app.database.connection import SessionLocal


def score_lead_agent(lead_id: int) -> LeadDB | None:
    db = SessionLocal()
    try:
        lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
        if not lead:
            return None

        enrichment = {"employee_count": lead.employee_count}
        signals = {"buying_signals": json.loads(lead.buying_signals or "[]")}
        qualification = json.loads(lead.qualification_details or "{}")

        result = calculate_score(
            enrichment=enrichment,
            signals=signals,
            qualification=qualification,
            job_title=lead.job_title
        )

        lead.lead_score = result["score"]
        lead.lead_priority = result["priority"]
        lead.score_breakdown = json.dumps(result["breakdown"])
        db.commit()
        db.refresh(lead)
        return lead
    finally:
        db.close()
