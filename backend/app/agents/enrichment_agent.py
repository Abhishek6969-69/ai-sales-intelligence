import json

from app.services.company_research import research_company
from app.services.llm_service import extract_company_data
from app.database.models import LeadDB
from app.database.connection import SessionLocal


def enrich_lead(lead_id: int):
    db = SessionLocal()

    try:
        lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()

        if not lead:
            return None

        research = research_company(lead.company)

        pages = research.get("pages", [])

        research_parts = []

        for page in pages:
            content = page.get("content", "")[:2000]

            research_parts.append(
                f"TITLE: {page['title']}\n"
                f"URL: {page['url']}\n"
                f"CONTENT:\n{content}"
            )

        research_text = "\n\n".join(research_parts)

        enrichment = extract_company_data(
            company=lead.company,
            research=research_text
        )

        lead.industry = enrichment.get("industry")
        lead.employee_count = enrichment.get("employee_count")
        lead.location = enrichment.get("location")
        lead.founded_year = enrichment.get("founded_year")

        lead.technologies = json.dumps(
            enrichment.get("technologies", [])
        )

        lead.revenue_range = enrichment.get("revenue_range")

        db.commit()
        db.refresh(lead)

        return lead

    finally:
        db.close()