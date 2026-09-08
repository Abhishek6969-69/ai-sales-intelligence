import os
import json

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_company_data(company: str, research: str):
    prompt = f"""
You are a company research data extraction system.

Company:
{company}

Research:
{research}

Extract only information explicitly supported by the research.

Return valid JSON with exactly these fields:

{{
    "industry": null,
    "employee_count": null,
    "location": null,
    "founded_year": null,
    "technologies": [],
    "revenue_range": null
}}

Rules:
- Do not guess.
- Do not invent missing information.
- Use null when information is unavailable.
- employee_count must be an integer or null.
- founded_year must be an integer or null.
- technologies must be an array of strings.
- Return JSON only.
"""

    response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0
)

    content = response.choices[0].message.content

    return json.loads(content)