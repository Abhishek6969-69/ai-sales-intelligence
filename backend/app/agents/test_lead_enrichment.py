from app.agents.enrichment_agent import enrich_lead


lead = enrich_lead(1)

if lead:
    print("LEAD ENRICHED")
    print("Company:", lead.company)
    print("Industry:", lead.industry)
    print("Employees:", lead.employee_count)
    print("Location:", lead.location)
    print("Founded:", lead.founded_year)
    print("Technologies:", lead.technologies)
    print("Revenue:", lead.revenue_range)
else:
    print("Lead not found")