from app.agents.research_agent import research_lead_agent


result = research_lead_agent(
    name="Rahul Sharma",
    job_title="VP Sales",
    company="Stripe"
)

print("LEAD RESEARCH RESULT:")
print(result)