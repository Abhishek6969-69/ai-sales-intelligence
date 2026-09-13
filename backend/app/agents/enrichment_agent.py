import json
from datetime import datetime

from app.services.company_research import research_company, research_company_signals
from app.services.llm_service import extract_company_data, extract_buying_signals, qualify_lead
from app.services.scoring_engine import calculate_score
from app.database.models import LeadDB
from app.database.connection import SessionLocal


def _pages_to_text(pages: list, max_chars_per_page: int = 2000) -> str:
    parts = []
    for page in pages:
        content = page.get("content", "")[:max_chars_per_page]
        parts.append(
            f"TITLE: {page['title']}\nURL: {page['url']}\nCONTENT:\n{content}"
        )
    return "\n\n".join(parts)


def enrich_lead(lead_id: int) -> LeadDB | None:
    db = SessionLocal()

    try:
        lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
        if not lead:
            return None

        # ── STEP 1: Company enrichment ─────────────────────────────────────
        company_research = research_company(lead.company)
        research_text = _pages_to_text(company_research.get("pages", []))

        enrichment = extract_company_data(
            company=lead.company,
            research=research_text
        )

        lead.industry = enrichment.get("industry")
        lead.employee_count = enrichment.get("employee_count")
        lead.location = enrichment.get("location")
        lead.founded_year = enrichment.get("founded_year")
        lead.technologies = json.dumps(enrichment.get("technologies", []))
        lead.revenue_range = enrichment.get("revenue_range")
        lead.key_executives = json.dumps(enrichment.get("key_executives", []))
        lead.status = "enriched"
        db.commit()

        # ── STEP 2: Buying signals research ───────────────────────────────
        signals_research = research_company_signals(lead.company)
        signals_text = _pages_to_text(signals_research.get("pages", []))

        signals = extract_buying_signals(
            company=lead.company,
            research=signals_text
        )

        lead.buying_signals = json.dumps(signals.get("buying_signals", []))
        lead.pain_points = json.dumps(signals.get("pain_points", []))
        lead.product_fit = signals.get("product_fit")
        db.commit()

        # ── STEP 3: Qualification ─────────────────────────────────────────
        qualification = qualify_lead(
            enrichment=enrichment,
            signals=signals
        )

        lead.qualification_verdict = qualification.get("verdict")
        lead.qualification_details = json.dumps(qualification)
        lead.status = "qualified"
        db.commit()

        # ── STEP 4: Deterministic scoring ─────────────────────────────────
        result = calculate_score(
            enrichment=enrichment,
            signals=signals,
            qualification=qualification,
            job_title=lead.job_title
        )

        lead.lead_score = result["score"]
        lead.lead_priority = result["priority"]
        lead.score_breakdown = json.dumps(result["breakdown"])
        lead.enriched_at = datetime.utcnow()
        lead.status = "scored"
        db.commit()
        db.refresh(lead)

        return lead

    finally:
        db.close()