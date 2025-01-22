import httpx
import logging
from models import CodeExecutionResult, TestCase
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

async def execute_code(code: str, language: str, input: str) -> CodeExecutionResult:
    """
    Execute the code using an external API.
    """
    url = 'https://dev-coderunner-q4twihl4ya-as.a.run.app/api/execute'
    payload = {
        'script': code,
        'language': language,
    }
    if input:
        payload['stdin'] = input
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJjWm5DVEk0RE5lUENwMjNuYWROei1BQmF0MGJ1dDgwTkctMDhOeHR2eFBvIn0.eyJleHAiOjE3Mzc3ODUzMTcsImlhdCI6MTczNzUyNjExNywiYXV0aF90aW1lIjoxNzM3NTI2MTE3LCJqdGkiOiIwYWU3MzM5OS0yOWJjLTQzMTQtOTFkNS0zNDViNzgzZjAxODciLCJpc3MiOiJodHRwczovL2F1dGgua2Fsdml1bS5jb21tdW5pdHkvYXV0aC9yZWFsbXMva2Fsdml1bS1kZXYiLCJzdWIiOiIzMzMxYTJhOS0xODEwLTQ0ZGYtOWQ2My04YzFjYzRlZjU4MjkiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ0ZXN0LW5leHRqcy1hcHAiLCJzZXNzaW9uX3N0YXRlIjoiNTAzNTdkNzItYTg1Yi00NzY0LWEyMWYtNDlkZDg2MzY1NDI1IiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLWthbHZpdW0tZGV2IiwiZWFybHktYWNjZXNzIiwibWVudG9yIiwic3R1ZGVudHBsdXMiLCJzdHVkZW50IiwiYXV0aG9yIl19LCJzY29wZSI6Im9wZW5pZCBtYWNoaW5lLXJvbGUgZW1haWwgcHJvZmlsZSByb2xlcyIsInNpZCI6IjUwMzU3ZDcyLWE4NWItNDc2NC1hMjFmLTQ5ZGQ4NjM2NTQyNSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYW1lIjoiSXNoYW4gUyIsInByZWZlcnJlZF91c2VybmFtZSI6ImlzaGFuLnNAa2Fsdml1bS5jb20iLCJnaXZlbl9uYW1lIjoiSXNoYW4iLCJmYW1pbHlfbmFtZSI6IlMiLCJlbWFpbCI6ImlzaGFuLnNAa2Fsdml1bS5jb20ifQ.Ytg-Wrj59BFKcDZX7ildMYAuWLXEjJns5ijQHEnL6Q8BGwBtsUBRm9qwZ-Wl8Mtaibwrgyw0cxH0KRMNLls-z7xvRX4Xy8FPnUbublkR2SLaC2I4Xtp2FFy7i-kublizYGwD9yA-YJbj2icMAGoBC28MIPSdzXmVnvBCSOVXxzJbNn2T-przcVwoZCT_wQoGok4mwmotlv-rpN_yGKazMtqiZCY-w5FY5u_6N25bZpJOHanrbQ7xaldwB2WpDdKrLVramc9-5VxP5lQklOMxYlQILj2pzxCScfFKGxjpeyEFMcq8YROCwS3sEKF2r4ETFbSRXqSBvbBLVYHW7oDz5A'}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, headers=headers, timeout=30)  # Add timeout
            response.raise_for_status()  # Raise HTTP errors
            response_data = response.json()
            logger.info(f"Response data: {response_data}")
            return CodeExecutionResult(
                output=response_data['output'],
                error=response_data['error']
            )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
        return CodeExecutionResult(output='', error=2)
    except Exception as e:
        logger.error(f"Execution error occurred: {e}")
        return CodeExecutionResult(output='', error=3)

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