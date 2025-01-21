import httpx
import logging
from models import CodeExecutionResult, TestCase
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

async def execute_code(code: str, language: str, input_json: str = "{}") -> CodeExecutionResult:
    """
    Execute the code using an external API.
    """
    url = 'https://dev-coderunner-q4twihl4ya-as.a.run.app/api/execute'
    payload = {
        'script': code,
        'language': language,
        'stdin': input_json  # Pass input as a JSON string
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJjWm5DVEk0RE5lUENwMjNuYWROei1BQmF0MGJ1dDgwTkctMDhOeHR2eFBvIn0.eyJleHAiOjE3Mzc3NDQ4NzUsImlhdCI6MTczNzQ4NTY3NSwiYXV0aF90aW1lIjoxNzM3NDg1Njc1LCJqdGkiOiIzNzQyY2RlZS0wMDY2LTQ5NzgtYmFhMS1mY2VlNTI0MTliY2UiLCJpc3MiOiJodHRwczovL2F1dGgua2Fsdml1bS5jb21tdW5pdHkvYXV0aC9yZWFsbXMva2Fsdml1bS1kZXYiLCJzdWIiOiIzMzMxYTJhOS0xODEwLTQ0ZGYtOWQ2My04YzFjYzRlZjU4MjkiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ0ZXN0LW5leHRqcy1hcHAiLCJzZXNzaW9uX3N0YXRlIjoiZGU1MjRjODQtYjFkMC00N2MzLWJiM2MtY2MyNjFmZjhmODg0IiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLWthbHZpdW0tZGV2IiwiZWFybHktYWNjZXNzIiwibWVudG9yIiwic3R1ZGVudHBsdXMiLCJzdHVkZW50IiwiYXV0aG9yIl19LCJzY29wZSI6Im9wZW5pZCBtYWNoaW5lLXJvbGUgZW1haWwgcHJvZmlsZSByb2xlcyIsInNpZCI6ImRlNTI0Yzg0LWIxZDAtNDdjMy1iYjNjLWNjMjYxZmY4Zjg4NCIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYW1lIjoiSXNoYW4gUyIsInByZWZlcnJlZF91c2VybmFtZSI6ImlzaGFuLnNAa2Fsdml1bS5jb20iLCJnaXZlbl9uYW1lIjoiSXNoYW4iLCJmYW1pbHlfbmFtZSI6IlMiLCJlbWFpbCI6ImlzaGFuLnNAa2Fsdml1bS5jb20ifQ.HKnR2bD8ScCwgFkkkY1desxigJupDfh32PF93rp0SANWxX2QpPsO09E5HqasNRGoQc8EevTSXHZ0uMwIcwcMN20jAa3-1-kRv-CvQGulnvn_TVVxrn4Rg2dzrAsbzjD7t6-5zdPi97B5gkLV4WgqmdoIG6ud_GM5LA4mEOWRaED1Ep5UXNCUWe5w0TJJFzibwkrdDtEAac6fnJuaepO_z7X0ecYOHlQ5DuG3b2R0sm9vL0Fz86zipDGcD-mhcfLELTn5CZ4irGyG6rpXY3ZpmYa9BXxJTgqNahWK_VIjitGdUdMGJMNa6PEVWMW4Cf_gShgmbISyHoAKofKsr5lorw'}

    logger.info(f"payload: {payload}")

    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, headers=headers, timeout=30)  # Add timeout
            response.raise_for_status()  # Raise HTTP errors
            response_data = response.json()
            logger.info(f"Response data: {response_data}")
            return CodeExecutionResult(
                output=response_data['output'],
                error=response_data['errorMessage']
            )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
        return CodeExecutionResult(output='', error=f"HTTP Error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Execution error occurred: {e}")
        return CodeExecutionResult(output='', error=f"Execution Error: {str(e)}")

async def validate_test_cases(code: str, language: str, test_cases: List[TestCase]) -> List[Dict[str, Any]]:
    """Validate the code against all test cases"""
    test_results = []
    for test_case in test_cases:
        execution_result = await execute_code(code, language, test_case.input)
        test_results.append({
            "input": test_case.input,
            "expected_output": test_case.expected_output,
            "actual_output": execution_result.output,
            "passed": execution_result.output.strip() == test_case.expected_output.strip(),
            "error": execution_result.error
        })
    return test_results