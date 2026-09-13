from datetime import datetime

from app.services.pipeline_service import calculate_expected_revenue, flag_at_risk
from app.services.scoring_engine import get_stage_probability
from app.database.models import PipelineDB, LeadDB
from app.database.connection import SessionLocal


def process_pipeline_entry(pipeline_id: int) -> PipelineDB | None:
    db = SessionLocal()
    try:
        entry = db.query(PipelineDB).filter(PipelineDB.id == pipeline_id).first()
        if not entry:
            return None

        entry_dict = {
            "deal_value": entry.deal_value,
            "deal_stage": entry.deal_stage,
            "probability": entry.probability,
            "days_in_stage": entry.days_in_stage,
            "meeting_count": entry.meeting_count,
            "email_engagement": entry.email_engagement,
        }

        prob = entry.probability or get_stage_probability(entry.deal_stage)
        entry.expected_revenue = calculate_expected_revenue(entry.deal_value, prob)

        risk = flag_at_risk(entry_dict)
        entry.at_risk = risk["at_risk"]
        entry.risk_reason = risk["risk_reason"]

        entry.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(entry)

        return entry
    finally:
        db.close()
