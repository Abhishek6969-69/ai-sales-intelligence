from fastapi import APIRouter
from app.models.lead import Lead

router = APIRouter()

leads = []


@router.post("/leads")
def create_lead(lead: Lead):
    leads.append(lead)

    return {
        "message": "Lead created successfully",
        "lead": lead
    }


@router.get("/leads")
def get_leads():
    return leads