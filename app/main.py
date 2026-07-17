from typing import List, Dict, Any
from fastapi import FastAPI

from app.parser import parse_payload

app = FastAPI(
    title="Email Parser API",
    version="1.0.0"
)


@app.get("/health")
def health():
    return {"status": "UP"}


@app.post("/parse-email")
async def parse_email(payload: List[Dict[str, Any]]):

    result = parse_payload(payload)

    return result