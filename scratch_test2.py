from app.llm import generate_tests
from app.runner import run_tests

source = """
def add(a, b):
    return a + b
"""

gen = generate_tests(source)
print("LLM output:", gen)

result = run_tests(source, gen["tests"])
print("Run result:", result)

from app.evaluator import evaluate_result

evaluation = evaluate_result(result, gen)
print("Evaluation:", evaluation)