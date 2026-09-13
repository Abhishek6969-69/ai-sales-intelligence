import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def run_migration():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    migrations = [
        # Enrichment additions
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS key_executives TEXT;",
        # Signals
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS buying_signals TEXT;",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS pain_points TEXT;",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS product_fit VARCHAR(20);",
        # Qualification
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS qualification_verdict VARCHAR(20);",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS qualification_details TEXT;",
        # Scoring
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS lead_score INTEGER DEFAULT 0;",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS lead_priority VARCHAR(20);",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS score_breakdown TEXT;",
        # Competitor
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS competitor VARCHAR(200);",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS competitor_weakness TEXT;",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS opportunity TEXT;",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS positioning TEXT;",
        # Outreach
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS outreach_subject VARCHAR(500);",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS outreach_body TEXT;",
        # Meta
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'new';",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS enriched_at TIMESTAMP;",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();",
        # Pipeline table
        """
        CREATE TABLE IF NOT EXISTS pipeline (
            id SERIAL PRIMARY KEY,
            lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
            deal_stage VARCHAR(50) NOT NULL,
            deal_value FLOAT NOT NULL,
            close_date VARCHAR(20),
            probability FLOAT,
            sales_activity_score INTEGER DEFAULT 0,
            meeting_count INTEGER DEFAULT 0,
            email_engagement INTEGER DEFAULT 0,
            days_in_stage INTEGER DEFAULT 0,
            at_risk BOOLEAN DEFAULT FALSE,
            risk_reason TEXT,
            expected_revenue FLOAT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
    ]

    for sql in migrations:
        try:
            cur.execute(sql)
            conn.commit()
            print(f"OK: {sql[:60].strip()}...")
        except Exception as e:
            conn.rollback()
            print(f"SKIP (already exists or error): {e}")

    cur.close()
    conn.close()
    print("Migration complete.")


if __name__ == "__main__":
    run_migration()