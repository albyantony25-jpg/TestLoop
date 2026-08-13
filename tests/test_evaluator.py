from app.evaluator import evaluate_result

dummy_llm_output = {
    "tests": "def test_foo(): pass",
    "reasoning": "dummy reasoning",
    "confidence": 1.0,
    "needs_retry": False,
}


def test_evaluate_result_passed():
    run_result = {
        "passed": True,
        "exit_code": 0,
        "stdout": "1 passed",
        "stderr": "",
    }
    evaluation = evaluate_result(run_result, dummy_llm_output)
    assert evaluation["is_good"] is True
    assert "passed" in evaluation["reason"].lower()


def test_evaluate_result_test_failure():
    run_result = {
        "passed": False,
        "exit_code": 1,
        "stdout": "FAILED test_solution.py::test_add - assert 1 == 2",
        "stderr": "",
    }
    evaluation = evaluate_result(run_result, dummy_llm_output)
    assert evaluation["is_good"] is False
    assert "some tests failed" in evaluation["reason"].lower()


def test_evaluate_result_collection_error():
    run_result = {
        "passed": False,
        "exit_code": 2,
        "stdout": "ERROR collecting test_solution.py\nSyntaxError: invalid syntax",
        "stderr": "",
    }
    evaluation = evaluate_result(run_result, dummy_llm_output)
    assert evaluation["is_good"] is False
    assert "collection error" in evaluation["reason"].lower()
