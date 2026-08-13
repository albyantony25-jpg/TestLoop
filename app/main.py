import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.agent import run_agent_loop
from app.models import GenerateTestsRequest, GenerateTestsResponse

app = FastAPI()

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return FileResponse("static/index.html")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/generate-tests", response_model=GenerateTestsResponse)
def generate_tests_endpoint(request: GenerateTestsRequest):
    state = run_agent_loop(request.source_code)
    history = state.get("history", [])

    last_tests = history[-1]["llm_output"].get("tests", "") if history else ""
    last_eval_reason = history[-1]["evaluation"].get("reason", "") if history else ""

    return GenerateTestsResponse(
        success=state.get("success", False),
        iterations=state.get("iterations", len(history)),
        tests=last_tests,
        evaluation=last_eval_reason,
        history=history,
    )


