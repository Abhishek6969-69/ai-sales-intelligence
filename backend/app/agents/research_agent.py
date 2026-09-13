from app.services.lead_research import research_lead


def research_lead_agent(name: str, job_title: str, company: str):
    return research_lead(
        name=name,
        job_title=job_title,
        company=company
    )