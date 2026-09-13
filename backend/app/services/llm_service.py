import os
import json
import re

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-20b"


def _call_llm(prompt: str, temperature: float = 0) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content


def _parse_json(content: str) -> dict:
    """Robustly parse JSON from LLM output (handles markdown code fences)."""
    content = content.strip()
    # Strip markdown code fences if present
    content = re.sub(r'^```(?:json)?\s*', '', content, flags=re.MULTILINE)
    content = re.sub(r'```\s*$', '', content, flags=re.MULTILINE)
    return json.loads(content.strip())


def extract_company_data(company: str, research: str) -> dict:
    prompt = f"""
You are a company research data extraction system.

Company: {company}

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
    "revenue_range": null,
    "key_executives": []
}}

Rules:
- Do not guess. Do not invent missing information.
- Use null when information is unavailable.
- employee_count must be an integer or null.
- founded_year must be an integer or null.
- technologies must be an array of strings.
- key_executives must be an array of strings (name + title when available).
- Return JSON only, no markdown.
"""
    return _parse_json(_call_llm(prompt))


def extract_buying_signals(company: str, research: str) -> dict:
    prompt = f"""
You are a sales intelligence analyst identifying buying signals.

Company: {company}

Research:
{research}

Identify active sales signals that indicate timing and purchase intent.

Return valid JSON with exactly these fields:
{{
    "buying_signals": [],
    "pain_points": [],
    "product_fit": null
}}

Rules:
- buying_signals: array of specific, evidence-backed signal strings (e.g. "Raised $30M Series B in March 2024", "Actively hiring 50 cloud engineers")
- pain_points: array of likely business pain points inferred from the signals
- product_fit: "High", "Medium", "Low", or null based on overall signal strength
- Only include signals supported by the research. No guessing.
- Return JSON only, no markdown.
"""
    return _parse_json(_call_llm(prompt))


def qualify_lead(enrichment: dict, signals: dict) -> dict:
    """
    ICP criteria:
    - Industry: SaaS / FinTech / Cloud / Tech (industry_fit)
    - Employees: 200+ (size_fit)
    - Location: US / India / Europe (location_fit)
    - Technology: cloud-based stack (tech_fit)
    - Revenue: $10M+ (revenue_fit)
    - Growth: actively growing (growth_fit)
    """
    prompt = f"""
You are a lead qualification specialist.

Lead Enrichment Data:
{json.dumps(enrichment, indent=2)}

Buying Signals:
{json.dumps(signals, indent=2)}

Ideal Customer Profile (ICP):
- Industry: SaaS, FinTech, Cloud, Technology
- Employees: 200 or more
- Location: US, India, or Europe
- Technology: Cloud-based stack (AWS/GCP/Azure, modern frameworks)
- Annual Revenue: $10M or more
- Growth: Actively growing company

Evaluate each criterion and return valid JSON:
{{
    "industry_fit": false,
    "size_fit": false,
    "location_fit": false,
    "tech_fit": false,
    "revenue_fit": false,
    "growth_fit": false,
    "verdict": null,
    "reason": null
}}

Rules:
- Each criterion must be true or false.
- verdict must be "HIGH", "MEDIUM", "LOW", or "DISQUALIFIED".
  - HIGH: 5-6 criteria met
  - MEDIUM: 3-4 criteria met
  - LOW: 1-2 criteria met
  - DISQUALIFIED: 0 criteria met
- reason: one sentence explaining the verdict.
- Return JSON only, no markdown.
"""
    return _parse_json(_call_llm(prompt))


def analyze_competitor(company: str, research: str, product_category: str = "cloud observability platform") -> dict:
    prompt = f"""
You are a competitive intelligence analyst.

Company: {company}
Our Product Category: {product_category}

Research about the company:
{research}

Analyze what solutions the company currently uses and identify competitive opportunities.

Return valid JSON with exactly these fields:
{{
    "competitor": null,
    "competitor_weakness": null,
    "opportunity": null,
    "positioning": null
}}

Rules:
- competitor: name of the tool/vendor the company currently uses (or "Unknown" if not found)
- competitor_weakness: specific weakness of their current solution based on their profile
- opportunity: the specific gap our product fills for this company
- positioning: one tactical recommendation for how to position against their current solution
- Base everything on the research. Do not invent details.
- Return JSON only, no markdown.
"""
    return _parse_json(_call_llm(prompt))


def generate_outreach(lead_data: dict) -> dict:
    buying_signals = lead_data.get("buying_signals", [])
    pain_points = lead_data.get("pain_points", [])
    positioning = lead_data.get("positioning", "")
    competitor = lead_data.get("competitor", "")
    company = lead_data.get("company", "")
    name = lead_data.get("name", "")
    job_title = lead_data.get("job_title", "")
    industry = lead_data.get("industry", "")

    prompt = f"""
You are an expert B2B sales copywriter.

Write a personalized cold outreach email for:
Name: {name}
Title: {job_title}
Company: {company}
Industry: {industry}

Buying Signals:
{json.dumps(buying_signals, indent=2)}

Pain Points:
{json.dumps(pain_points, indent=2)}

Competitor they currently use: {competitor}
Our positioning angle: {positioning}

Instructions:
- Reference 1-2 specific buying signals in the email body (be concrete, not generic)
- Keep the body under 150 words
- Focus on value, not features
- Do NOT use generic openers like "I hope this email finds you well"
- Sound human and conversational

Return valid JSON:
{{
    "subject": null,
    "body": null
}}

Return JSON only, no markdown.
"""
    return _parse_json(_call_llm(prompt, temperature=0.3))