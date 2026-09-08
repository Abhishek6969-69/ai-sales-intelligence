from app.services.llm_service import extract_company_data


research = """
Stripe is a financial infrastructure platform for businesses.
Stripe was founded in 2010 and is headquartered in San Francisco.
The company operates globally.
"""

result = extract_company_data(
    "Stripe",
    research
)

print(result)