from unittest.mock import patch

from app.agent import MAX_ITERATIONS, run_agent_loop

# Note: Real external API calls to Groq in app.llm.generate_tests are mocked out in these tests.
# Automated tests avoid real API calls to ensure deterministic execution, fast feedback, and zero API costs.


def test_agent_loop_success_first_attempt():
    source_code = "def add(a, b):\n    return a + b"
    llm_response = {
        "tests": "def test_add():\n    assert add(1, 2) == 3",
        "reasoning": "Simple addition test",
        "confidence": 1.0,
        "needs_retry": False,
    }

    with patch("app.agent.generate_tests", return_value=llm_response):
        state = run_agent_loop(source_code)
        assert state["success"] is True
        assert state["iterations"] == 1
        assert len(state["history"]) == 1


def test_agent_loop_max_iterations_failure():
    source_code = "def add(a, b):\n    return a + b"
    llm_response = {
        "tests": "def test_add():\n    assert add(1, 2) == 99",
        "reasoning": "Failing test",
        "confidence": 0.5,
        "needs_retry": True,
    }

    with patch("app.agent.generate_tests", return_value=llm_response):
        state = run_agent_loop(source_code)
        assert state["success"] is False
        assert state["iterations"] == MAX_ITERATIONS
        assert len(state["history"]) == MAX_ITERATIONS


def test_agent_loop_retry_success():
    source_code = "def add(a, b):\n    return a + b"
    fail_response = {
        "tests": "def test_add():\n    assert add(1, 2) == 99",
        "reasoning": "Wrong assertion",
        "confidence": 0.5,
        "needs_retry": True,
    }
    pass_response = {
        "tests": "def test_add():\n    assert add(1, 2) == 3",
        "reasoning": "Correct assertion",
        "confidence": 1.0,
        "needs_retry": False,
    }

    with patch("app.agent.generate_tests", side_effect=[fail_response, pass_response]) as mock_gen:
        state = run_agent_loop(source_code)
        assert state["success"] is True
        assert state["iterations"] == 2
        assert len(state["history"]) == 2

        # Verify previous_failure argument on second call
        second_call = mock_gen.call_args_list[1]
        assert second_call.kwargs.get("previous_failure") is not None
