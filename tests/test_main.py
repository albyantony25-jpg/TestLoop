from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "TestLoop" in response.text


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}



def test_generate_tests_endpoint():
    mock_agent_state = {
        "success": True,
        "iterations": 1,
        "source_code": "def add(a, b):\n    return a + b",
        "history": [
            {
                "iteration": 1,
                "llm_output": {
                    "tests": "def test_add():\n    assert add(1, 2) == 3",
                    "reasoning": "Generated test for addition",
                    "confidence": 1.0,
                    "needs_retry": False,
                },
                "run_result": {
                    "passed": True,
                    "exit_code": 0,
                    "stdout": "1 passed",
                    "stderr": "",
                },
                "evaluation": {
                    "is_good": True,
                    "reason": "All tests passed.",
                },
            }
        ],
    }

    with patch("app.main.run_agent_loop", return_value=mock_agent_state):
        response = client.post("/generate-tests", json={"source_code": "def add(a, b):\n    return a + b"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["iterations"] == 1
        assert data["tests"] == "def test_add():\n    assert add(1, 2) == 3"
        assert data["evaluation"] == "All tests passed."
        assert isinstance(data["history"], list)
        assert len(data["history"]) == 1
