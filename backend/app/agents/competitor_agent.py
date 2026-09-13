import json

from app.services.company_research import research_company_competitor
from app.services.llm_service import analyze_competitor
from app.database.models import LeadDB
from app.database.connection import SessionLocal


def _pages_to_text(pages: list, max_chars: int = 1500) -> str:
    parts = []
    for page in pages:
        content = page.get("content", "")[:max_chars]
        parts.append(f"TITLE: {page['title']}\nCONTENT:\n{content}")
    return "\n\n".join(parts)


def analyze_competitor_agent(lead_id: int) -> LeadDB | None:
    db = SessionLocal()
    try:
        lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
        if not lead:
            return None

        research = research_company_competitor(lead.company)
        research_text = _pages_to_text(research.get("pages", []))

        # Merge with existing enrichment context
        enrichment_context = (
            f"Industry: {lead.industry}\n"
            f"Technologies: {lead.technologies}\n"
            f"Employee count: {lead.employee_count}\n"
        )
        full_context = enrichment_context + "\n\n" + research_text

        result = analyze_competitor(company=lead.company, research=full_context)

        lead.competitor = result.get("competitor")
        lead.competitor_weakness = result.get("competitor_weakness")
        lead.opportunity = result.get("opportunity")
        lead.positioning = result.get("positioning")
        db.commit()
        db.refresh(lead)

        return lead
    finally:
        db.close()
