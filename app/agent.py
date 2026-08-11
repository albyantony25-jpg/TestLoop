from app.evaluator import evaluate_result
from app.llm import generate_tests
from app.logger import logger
from app.runner import run_tests

MAX_ITERATIONS = 3


def run_agent_loop(source_code: str) -> dict:
    """Runs the self-correcting agent loop for test generation and evaluation.

    Loops up to MAX_ITERATIONS times to generate, run, and evaluate tests.

    Returns:
        dict: {
            "success": bool,
            "iterations": int,
            "source_code": str,
            "history": list[dict]
        }
    """
    history = []
    success = False
    previous_failure = None

    for iteration in range(1, MAX_ITERATIONS + 1):
        logger.info(f"Iteration {iteration}\n───────────")

        llm_output = generate_tests(source_code, previous_failure=previous_failure)
        logger.info("Generated tests")

        logger.info("Running pytest...")
        run_result = run_tests(source_code, llm_output.get("tests", ""))
        logger.info(f"Pytest run completed - Passed: {run_result.get('passed')}")

        evaluation = evaluate_result(run_result, llm_output)

        step = {
            "iteration": iteration,
            "llm_output": llm_output,
            "run_result": run_result,
            "evaluation": evaluation,
        }
        history.append(step)

        if evaluation.get("is_good"):
            logger.info("Finished.")
            success = True
            break

        logger.info("Analyzing failure...")

        stdout = run_result.get("stdout", "")
        stderr = run_result.get("stderr", "")
        previous_failure = stderr if stderr else stdout

    return {
        "success": success,
        "iterations": len(history),
        "source_code": source_code,
        "history": history,
    }

