from app.services.scoring_engine import get_stage_probability


def calculate_expected_revenue(deal_value: float, probability: float) -> float:
    return round(deal_value * probability, 2)


def flag_at_risk(pipeline_entry: dict) -> dict:
    """
    Returns {at_risk: bool, risk_reason: str}
    At-risk conditions:
    - High value deal (>= $100K) stuck for >30 days in same stage
    - Any deal stuck >45 days
    - High value deal with low activity (meeting_count == 0 AND email_engagement == 0)
    """
    reasons = []
    deal_value = pipeline_entry.get("deal_value", 0)
    days_in_stage = pipeline_entry.get("days_in_stage", 0)
    meeting_count = pipeline_entry.get("meeting_count", 0)
    email_engagement = pipeline_entry.get("email_engagement", 0)
    deal_stage = pipeline_entry.get("deal_stage", "").lower()

    # Skip closed deals
    if deal_stage in ("closed_won", "closed_lost"):
        return {"at_risk": False, "risk_reason": None}

    if deal_value >= 100000 and days_in_stage > 30:
        reasons.append(f"High-value deal (${deal_value:,.0f}) stagnant for {days_in_stage} days")

    if days_in_stage > 45:
        reasons.append(f"Deal stagnant for {days_in_stage} days")

    if deal_value >= 100000 and meeting_count == 0 and email_engagement == 0:
        reasons.append("No sales activity on high-value deal")

    at_risk = len(reasons) > 0
    return {
        "at_risk": at_risk,
        "risk_reason": "; ".join(reasons) if reasons else None
    }


def compute_forecast(pipeline_entries: list) -> dict:
    """
    Compute aggregate forecast from all pipeline entries.
    """
    total_pipeline = 0.0
    expected_revenue = 0.0
    best_case = 0.0
    at_risk_deals = []

    stage_probs = {
        "prospecting": 0.10,
        "qualification": 0.20,
        "proposal": 0.40,
        "negotiation": 0.70,
        "closed_won": 1.00,
        "closed_lost": 0.00,
    }

    for entry in pipeline_entries:
        stage = (entry.get("deal_stage") or "").lower()
        value = entry.get("deal_value") or 0
        prob = entry.get("probability") or stage_probs.get(stage, 0.10)

        if stage == "closed_lost":
            continue

        total_pipeline += value
        expected_revenue += value * prob
        # Best case: use 80% upside on current probability
        best_case += value * min(prob * 1.2, 1.0)

        if entry.get("at_risk"):
            at_risk_deals.append({
                "lead_id": entry.get("lead_id"),
                "deal_value": value,
                "risk_reason": entry.get("risk_reason"),
                "deal_stage": entry.get("deal_stage")
            })

    return {
        "total_pipeline": round(total_pipeline, 2),
        "expected_revenue": round(expected_revenue, 2),
        "best_case": round(best_case, 2),
        "at_risk_deals": at_risk_deals
    }
