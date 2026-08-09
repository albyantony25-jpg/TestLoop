from fastapi import FastAPI

from app.models import GenerateTestsRequest, GenerateTestsResponse

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/generate-tests", response_model=GenerateTestsResponse)
def generate_tests(request: GenerateTestsRequest):
    return GenerateTestsResponse(
        success=True,
        message=f"Received {len(request.source_code)} chars",
    )
