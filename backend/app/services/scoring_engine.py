from typing import Optional


DECISION_MAKER_TITLES = [
    "cto", "ceo", "coo", "vp", "vice president", "director", "head of",
    "chief", "founder", "co-founder", "president", "svp", "evp", "gm",
    "general manager", "engineering manager", "it manager"
]

STAGE_PROBABILITIES = {
    "prospecting": 0.10,
    "qualification": 0.20,
    "proposal": 0.40,
    "negotiation": 0.70,
    "closed_won": 1.00,
    "closed_lost": 0.00,
}


def is_decision_maker(job_title: Optional[str]) -> bool:
    if not job_title:
        return False
    title_lower = job_title.lower()
    return any(kw in title_lower for kw in DECISION_MAKER_TITLES)


def calculate_score(
    enrichment: dict,
    signals: dict,
    qualification: dict,
    job_title: Optional[str] = None
) -> dict:
    """
    Deterministic scoring engine — total 100 points.
    LLM is NOT involved here.

    Weights:
      industry_fit   20
      company_size   15
      tech_fit       20
      growth         15
      buying_signals 20
      decision_maker 10
    """
    score = 0
    breakdown = {}

    # 1. Industry fit (20 pts)
    industry_fit = qualification.get("industry_fit", False)
    industry_score = 20 if industry_fit else 0
    score += industry_score
    breakdown["industry_fit"] = {"score": industry_score, "max": 20}

    # 2. Company size (15 pts)
    employee_count = enrichment.get("employee_count") or 0
    if employee_count >= 1000:
        size_score = 15
    elif employee_count >= 500:
        size_score = 12
    elif employee_count >= 200:
        size_score = 10
    elif employee_count >= 50:
        size_score = 6
    elif employee_count > 0:
        size_score = 3
    else:
        size_score = 0
    score += size_score
    breakdown["company_size"] = {"score": size_score, "max": 15, "employees": employee_count}

    # 3. Tech fit (20 pts)
    tech_fit = qualification.get("tech_fit", False)
    tech_score = 20 if tech_fit else 0
    score += tech_score
    breakdown["tech_fit"] = {"score": tech_score, "max": 20}

    # 4. Growth signals (15 pts)
    buying_signals = signals.get("buying_signals", [])
    growth_keywords = ["funding", "hiring", "expansion", "growing", "raised", "launch", "new market", "acquisition"]
    growth_hit = sum(1 for sig in buying_signals if any(kw in sig.lower() for kw in growth_keywords))
    growth_fit = qualification.get("growth_fit", False)

    if growth_fit and growth_hit >= 2:
        growth_score = 15
    elif growth_fit or growth_hit >= 2:
        growth_score = 10
    elif growth_hit >= 1:
        growth_score = 5
    else:
        growth_score = 0
    score += growth_score
    breakdown["growth"] = {"score": growth_score, "max": 15, "growth_hits": growth_hit}

    # 5. Buying signals count (20 pts)
    signal_count = len(buying_signals)
    if signal_count >= 5:
        signal_score = 20
    elif signal_count >= 4:
        signal_score = 17
    elif signal_count >= 3:
        signal_score = 13
    elif signal_count >= 2:
        signal_score = 8
    elif signal_count >= 1:
        signal_score = 4
    else:
        signal_score = 0
    score += signal_score
    breakdown["buying_signals"] = {"score": signal_score, "max": 20, "count": signal_count}

    # 6. Decision maker (10 pts)
    dm = is_decision_maker(job_title)
    dm_score = 10 if dm else 0
    score += dm_score
    breakdown["decision_maker"] = {"score": dm_score, "max": 10, "is_decision_maker": dm}

    # Priority label
    if score >= 75:
        priority = "HOT"
    elif score >= 50:
        priority = "WARM"
    else:
        priority = "COLD"

    return {
        "score": score,
        "priority": priority,
        "breakdown": breakdown
    }


def get_stage_probability(stage: str) -> float:
    return STAGE_PROBABILITIES.get(stage.lower(), 0.10)
