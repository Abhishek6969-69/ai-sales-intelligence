from sqlalchemy import Column, Integer, String

from app.database.connection import Base


class LeadDB(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    company = Column(String, nullable=False)
    website = Column(String, nullable=True)
    job_title = Column(String, nullable=True)