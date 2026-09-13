import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database.connection import SessionLocal
from app.database.models import LeadDB
from app.agents.enrichment_agent import enrich_lead

def test():
    db = SessionLocal()
    # Find a lead with status="new"
    lead = db.query(LeadDB).filter(LeadDB.status == "new").first()
    if not lead:
        print("No new leads found")
        return
    
    print(f"Enriching lead: {lead.company} ({lead.id})")
    try:
        updated_lead = enrich_lead(lead.id)
        if updated_lead:
            print(f"Success! Status is now {updated_lead.status}")
        else:
            print("Failed to enrich")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
