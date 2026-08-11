from app.evaluator import evaluate_result
from app.llm import generate_tests
from app.runner import run_tests

MAX_ITERATIONS = 3


def run_agent_loop(source_code: str) -> dict:
    """Runs the self-correcting agent loop for test generation and evaluation.

    Loops up to MAX_ITERATIONS times to generate, run, and evaluate tests.

    Returns:
        dict: {
            "success": bool,
            "source_code": str,
            "history": list[dict]
        }
    """
    history = []
    success = False
    previous_failure = None

    for iteration in range(1, MAX_ITERATIONS + 1):
        llm_output = generate_tests(source_code, previous_failure=previous_failure)
        run_result = run_tests(source_code, llm_output.get("tests", ""))
        evaluation = evaluate_result(run_result, llm_output)

        step = {
            "iteration": iteration,
            "llm_output": llm_output,
            "run_result": run_result,
            "evaluation": evaluation,
        }
        history.append(step)

        if evaluation.get("is_good"):
            success = True
            break

        stdout = run_result.get("stdout", "")
        stderr = run_result.get("stderr", "")
        previous_failure = stderr if stderr else stdout

    return {
        "success": success,
        "source_code": source_code,
        "history": history,
    }
