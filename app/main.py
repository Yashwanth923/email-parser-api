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


@app.get("/version")
def version():
    return {
        "version": "multipart-support-v1"
    }


@app.post("/parse-email")
async def parse_email(request: Request):

    payload = await request.json()

    print("RAW PAYLOAD:")
    print(payload)

    if "$multipart" in payload:
        payload = payload["$multipart"]

    result = parse_payload(payload)

    print("RESULT:")
    print(result)

    return result