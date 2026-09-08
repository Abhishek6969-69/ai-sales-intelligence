from app.agents.enrichment_agent import enrich_company


result = enrich_company("Stripe")

print("ENRICHMENT RESULT:")
print(result)