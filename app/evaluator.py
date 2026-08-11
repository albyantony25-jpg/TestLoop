def evaluate_result(run_result: dict, llm_output: dict) -> dict:
    """Evaluates the outcome of running generated tests against source code.

    Args:
        run_result: dict containing keys 'passed' (bool), 'exit_code' (int), 'stdout' (str), 'stderr' (str).
        llm_output: dict containing keys 'tests' (str), 'reasoning' (str), 'confidence' (float), 'needs_retry' (bool).

    Returns:
        dict: {"is_good": bool, "reason": str}
    """
    if run_result.get("passed", False):
        return {"is_good": True, "reason": "All tests passed."}

    stdout = run_result.get("stdout", "")
    stdout_lower = stdout.lower()

    if (
        "error collecting" in stdout_lower
        or "errors during collection" in stdout_lower
        or "collection error" in stdout_lower
        or "syntaxerror" in stdout_lower
        or "importerror" in stdout_lower
        or ("error" in stdout and "collecting" in stdout_lower)
        or ("ERROR" in stdout and "collecting" in stdout_lower)
        or "interrupted: 1 error during collection" in stdout_lower
    ):
        return {"is_good": False, "reason": "Tests failed to run (collection error)."}

    return {"is_good": False, "reason": "Some tests failed."}
