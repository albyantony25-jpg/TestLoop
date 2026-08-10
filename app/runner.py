import os
import subprocess
import sys
import tempfile


def run_tests(source_code: str, test_code: str) -> dict:
    """Executes test_code against source_code in an isolated temporary directory using pytest.

    Returns:
        dict: {
            "passed": bool,
            "exit_code": int,
            "stdout": str,
            "stderr": str
        }
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        solution_path = os.path.join(temp_dir, "solution.py")
        test_solution_path = os.path.join(temp_dir, "test_solution.py")

        with open(solution_path, "w", encoding="utf-8") as f:
            f.write(source_code)

        with open(test_solution_path, "w", encoding="utf-8") as f:
            f.write(test_code)

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return {
                "passed": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired as e:
            stdout = e.stdout if isinstance(e.stdout, str) else (e.stdout.decode() if e.stdout else "")
            stderr = "Test execution timed out after 10 seconds."
            return {
                "passed": False,
                "exit_code": -1,
                "stdout": stdout,
                "stderr": stderr,
            }
