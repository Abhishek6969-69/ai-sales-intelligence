from app.services.lead_analysis import analyze_lead
from app.services.lead_research import research_lead


research = research_lead(
    name="Rahul Sharma",
    job_title="VP Sales",
    company="Stripe"
)

research_parts = []

for page in research.get("pages", []):
    content = page.get("content", "")[:1500]

    research_parts.append(
        f"TITLE: {page['title']}\n"
        f"URL: {page['url']}\n"
        f"CONTENT:\n{content}"
    )

research_text = "\n\n".join(research_parts)


result = analyze_lead(
    name="Rahul Sharma",
    job_title="VP Sales",
    company="Stripe",
    research=research_text
)

print("LEAD ANALYSIS RESULT:")
print(result)