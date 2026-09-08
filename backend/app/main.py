from fastapi import FastAPI

app = FastAPI(
    title="AI Sales Intelligence Platform",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "AI Sales Intelligence API is running"
    }