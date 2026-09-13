from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database.connection import Base


class LeadDB(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    # Basic lead info
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    company = Column(String, nullable=False)
    website = Column(String, nullable=True)
    job_title = Column(String, nullable=True)

    # Phase 1 — Enrichment
    industry = Column(String, nullable=True)
    employee_count = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
    founded_year = Column(Integer, nullable=True)
    technologies = Column(Text, nullable=True)       # JSON array
    revenue_range = Column(String, nullable=True)
    key_executives = Column(Text, nullable=True)     # JSON array

    # Phase 1 — Signals
    buying_signals = Column(Text, nullable=True)     # JSON array
    pain_points = Column(Text, nullable=True)        # JSON array
    product_fit = Column(String, nullable=True)      # High/Medium/Low

    # Phase 1 — Qualification
    qualification_verdict = Column(String, nullable=True)   # HIGH/MEDIUM/LOW/DISQUALIFIED
    qualification_details = Column(Text, nullable=True)     # JSON object

    # Phase 1 — Scoring
    lead_score = Column(Integer, nullable=True, default=0)
    lead_priority = Column(String, nullable=True)    # HOT/WARM/COLD
    score_breakdown = Column(Text, nullable=True)    # JSON object

    # Phase 2 — Competitor Analysis
    competitor = Column(String, nullable=True)
    competitor_weakness = Column(Text, nullable=True)
    opportunity = Column(Text, nullable=True)
    positioning = Column(Text, nullable=True)

    # Phase 2 — Outreach
    outreach_subject = Column(String, nullable=True)
    outreach_body = Column(Text, nullable=True)

    # Meta
    status = Column(String, nullable=True, default='new')  # new/enriched/qualified/scored
    enriched_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    pipeline = relationship("PipelineDB", back_populates="lead", uselist=False)


class PipelineDB(Base):
    __tablename__ = "pipeline"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)

    deal_stage = Column(String, nullable=False)      # prospecting/qualification/proposal/negotiation/closed_won/closed_lost
    deal_value = Column(Float, nullable=False)
    close_date = Column(String, nullable=True)       # ISO date string
    probability = Column(Float, nullable=True)       # 0.0 - 1.0

    sales_activity_score = Column(Integer, nullable=True, default=0)
    meeting_count = Column(Integer, nullable=True, default=0)
    email_engagement = Column(Integer, nullable=True, default=0)
    days_in_stage = Column(Integer, nullable=True, default=0)

    at_risk = Column(Boolean, nullable=True, default=False)
    risk_reason = Column(Text, nullable=True)
    expected_revenue = Column(Float, nullable=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lead = relationship("LeadDB", back_populates="pipeline")