from pydantic import BaseModel


class Lead(BaseModel):
    name: str
    email: str
    company: str
    website: str | None = None
    job_title: str | None = None