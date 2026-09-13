import os
import json

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_lead(
    name: str,
    job_title: str,
    company: str,
    research: str
):
    prompt = f"""
You are a sales intelligence analyst.

Lead:
Name: {name}
Job Title: {job_title}
Company: {company}

Research:
{research}

Analyze the research and return valid JSON with exactly these fields:

{{
    "current_role": null,
    "seniority": null,
    "responsibilities": [],
    "pain_points": [],
    "sales_opportunities": [],
    "relevance": null
}}

Rules:
- Use only information supported by the research.
- Do not guess.
- Do not invent facts.
- Ignore irrelevant search results.
- current_role should describe the person's role when supported.
- seniority should describe their level when supported.
- responsibilities must be an array of strings.
- pain_points must be an array of strings.
- sales_opportunities must be an array of strings.
- relevance should be "High", "Medium", "Low", or null.
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