from fastapi import FastAPI
from app.api.leads import router as leads_router

app = FastAPI(
    title="AI Sales Intelligence Platform",
    version="1.0.0"
)

app.include_router(leads_router)


@app.get("/")
def home():
    return {
        "message": "AI Sales Intelligence API is running"
    }