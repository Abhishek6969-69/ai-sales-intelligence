from app.services.company_research import research_company


result = research_company("Stripe")

print("Company:", result["company"])

for page in result["pages"]:
    print("\nTITLE:", page["title"])
    print("URL:", page["url"])
    print("CONTENT PREVIEW:")
    print(page["content"][:500])