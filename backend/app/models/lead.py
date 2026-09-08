from pydantic import BaseModel, EmailStr
from typing import Optional


class Lead(BaseModel):
    name: str
    email: EmailStr
    company: str
    website: Optional[str] = None
    job_title: Optional[str] = None