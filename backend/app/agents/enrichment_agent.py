from app.services.company_research import research_company
from app.services.llm_service import extract_company_data


def enrich_company(company: str):
    research = research_company(company)

    pages = research.get("pages", [])

    research_text = "\n\n".join(
        f"TITLE: {page['title']}\n"
        f"URL: {page['url']}\n"
        f"CONTENT:\n{page['content']}"
        for page in pages
    )

    return extract_company_data(
        company=company,
        research=research_text
    )