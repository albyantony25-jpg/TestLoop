# TestLoop

An autonomous Python test-generation agent that writes, executes, evaluates, and improves unit tests through a bounded feedback loop.

---

## Problem

Automated unit test generation using Large Language Models (LLMs) often suffers from key challenges:
- **Hallucinations & Syntax Errors**: LLMs can produce code containing syntax errors, invalid imports, or hallucinated APIs.
- **Lack of Verification**: Single-shot generation generates test code but never verifies whether the tests compile, run, or actually pass.
- **No Feedback Loop**: When generated tests fail, standard LLM generators have no mechanism to observe the failure logs and self-correct.

Generating valid unit tests requires **execution and feedback**, not just one-shot text generation.

---

## Solution

TestLoop addresses this by pairing LLM test generation with real execution and deterministic evaluation in an iterative feedback loop:

1. **LLM Generation**: Generates pytest unit tests from Python source code.
2. **Real Execution**: Runs the generated tests against the source code in an isolated temporary directory using `pytest`.
3. **Deterministic Evaluation**: Categorizes the outcome (success, test assertion failure, or collection/syntax error).
4. **Self-Correction Retry**: If tests fail or error, feeds the exact error output back to the LLM for a revised attempt.
5. **Bounded Loop**: Repeats up to `MAX_ITERATIONS = 3` to guarantee execution termination.

---

## Architecture

```text
+--------+      +-----------------+      +-----------------------------------------+      +----------------+
| Client | ---> | FastAPI Service | ---> |               Agent Loop                | ---> | Final Response |
+--------+      |  (/generate-   |      |          (MAX_ITERATIONS = 3)           |      +----------------+
                |     tests)      |      +-----------------------------------------+
                +-----------------+           |               |               |
                                              v               v               v
                                       +-------------+  +-----------+  +---------------+
                                       | LLM Service |  |  Pytest   |  | Deterministic |
                                       |   (Groq)    |  |  Runner   |  |   Evaluator   |
                                       +-------------+  +-----------+  +---------------+
```

---

## Agent Loop

The core self-correcting cycle follows five structured steps:

- **Generate**: The LLM writes pytest unit tests structured strictly as JSON.
- **Execute**: The runner writes `solution.py` and `test_solution.py` to a temporary directory and executes `pytest` as a subprocess with a 10-second timeout.
- **Observe**: Standard output (`stdout`) and error logs (`stderr`) are captured.
- **Evaluate**: Rules categorize execution into pass, failure, or collection error without extra LLM overhead.
- **Improve**: If tests fail, stderr/stdout feedback is appended to the prompt for the next LLM attempt.

---

## Tech Stack

- **Language**: Python 3.11+
- **API Framework**: [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- **Test Framework**: [pytest](https://docs.pytest.org/)
- **LLM Provider**: [Groq API](https://groq.com/) (`llama-3.3-70b-versatile`)
- **Environment Management**: `python-dotenv`
- **Validation & Models**: Pydantic v2

---

## Setup

### 1. Clone & Environment Setup
```bash
git clone https://github.com/albyantony25-jpg/TestLoop.git
cd TestLoop
python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set API Key
Create a `.env` file in the project root (see `.env.example`):
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 4. Run the API Server
```bash
uvicorn app.main:app --reload
```
Access the web UI at `http://127.0.0.1:8000/`. Interactive API docs are available at `http://127.0.0.1:8000/docs`.


### 5. Run the Automated Test Suite
```bash
pytest tests/
```

---

## Example

### Request
`POST /generate-tests`
```json
{
  "source_code": "def multiply(a, b):\n    return a * b"
}
```

### Response
```json
{
  "success": true,
  "iterations": 1,
  "tests": "from solution import multiply\n\ndef test_multiply_positive():\n    assert multiply(2, 3) == 6\n\ndef test_multiply_zero():\n    assert multiply(5, 0) == 0\n",
  "evaluation": "All tests passed.",
  "history": [
    {
      "iteration": 1,
      "llm_output": {
        "tests": "from solution import multiply\n...",
        "reasoning": "Basic multiplication tests",
        "confidence": 1.0,
        "needs_retry": false
      },
      "run_result": {
        "passed": true,
        "exit_code": 0,
        "stdout": "...",
        "stderr": ""
      },
      "evaluation": {
        "is_good": true,
        "reason": "All tests passed."
      }
    }
  ]
}
```

---

## Limitations

- **Non-Deterministic LLM Outputs**: Generated test code can vary between runs depending on LLM sampling.
- **Test Quality Variations**: Generated tests verify basic correctness but may occasionally omit edge cases or boundary conditions.
- **Subprocess Execution Safety**: Local subprocess execution is designed for local development. It does **not** provide full containerized sandboxing for untrusted code.
- **API Token Costs**: Each generation and retry consumes LLM API tokens.
- **Stateless Requests**: No persistent database storage; history is tracked per HTTP request.

---

## Future Improvements

- **Docker-based Sandboxing**: Execute generated tests inside isolated containers for safe multi-tenant execution.
- **Coverage-Guided Test Generation**: Feed code coverage metrics back into the agent to target untested execution paths.
- **Mutation Testing**: Run mutation analysis (e.g. `mutmut`) to measure true test suite quality.
- **GitHub Integration**: Connect to repositories to pull source files and open Pull Requests with generated tests automatically.
- **Multi-Provider Comparison**: Support switching or benchmarking between Groq, OpenAI, and Anthropic LLM models.
- **Web UI Dashboard**: Build a lightweight frontend interface to inspect loop state and test execution visually.
