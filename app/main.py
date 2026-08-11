from fastapi import FastAPI

from app.agent import run_agent_loop
from app.models import GenerateTestsRequest, GenerateTestsResponse

app = FastAPI()


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

