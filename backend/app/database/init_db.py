from app.database.connection import Base, engine
from app.database.models import LeadDB


Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")