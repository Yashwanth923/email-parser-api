from fastapi import FastAPI, Request

from app.parser import parse_payload

app = FastAPI(
    title="Email Parser API",
    version="1.0.0"
)


@app.get("/health")
def health():
    return {
        "status": "UP"
    }


@app.post("/parse-email")
async def parse_email(request: Request):

    payload = await request.json()

    if "$multipart" in payload:
        payload = payload["$multipart"]

    result = parse_payload(payload)

    print(result)

    return result