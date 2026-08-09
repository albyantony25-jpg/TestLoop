import json
import os
from dotenv import load_dotenv
from groq import Groq

from app.prompts import SYSTEM_PROMPT

load_dotenv()


def generate_tests(source_code: str) -> dict:
    """Sends source code to Groq LLM API to generate pytest unit tests.

    Returns parsed JSON dictionary with keys: tests, reasoning, confidence, needs_retry.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")

    client = Groq(api_key=api_key)

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": source_code},
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
        )
    except Exception as e:
        raise RuntimeError(f"Groq API call failed: {str(e)}") from e

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Received empty response from LLM API.")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}. Content: {content}") from e

    required_keys = {"tests", "reasoning", "confidence", "needs_retry"}
    missing_keys = required_keys - set(data.keys())
    if missing_keys:
        raise ValueError(f"LLM response missing required keys: {missing_keys}")

    return data
