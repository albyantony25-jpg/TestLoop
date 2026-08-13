from app.runner import run_tests


def test_run_tests_success():
    source_code = "def add(a, b):\n    return a + b"
    test_code = "def test_add():\n    assert add(1, 2) == 3"
    result = run_tests(source_code, test_code)
    assert result["passed"] is True
    assert result["exit_code"] == 0


def test_run_tests_failure():
    source_code = "def add(a, b):\n    return a - b"
    test_code = "def test_add():\n    assert add(1, 2) == 3"
    result = run_tests(source_code, test_code)
    assert result["passed"] is False
    assert result["exit_code"] != 0


def test_run_tests_syntax_error():
    source_code = "def add(a, b):\n    return a + b"
    test_code = "def test_add():\n    assert add(1, 2) == "
    result = run_tests(source_code, test_code)
    assert result["passed"] is False
    assert result["exit_code"] != 0
