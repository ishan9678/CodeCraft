import httpx
import logging
from models import CodeExecutionResult, TestCase
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

async def execute_code(code: str, language: str, input_json: str = "{}") -> CodeExecutionResult:
    """
    Execute the code using an external API.
    """
    url = 'https://api.codex.jaagrav.in'
    payload = {
        'code': code,
        'language': language,
        'input': input_json  # Pass input as a JSON string
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    logger.info(f"payload: {payload}")

    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, headers=headers, timeout=30)  # Add timeout
            response.raise_for_status()  # Raise HTTP errors
            response_data = response.json()
            logger.info(f"Response data: {response_data}")
            return CodeExecutionResult(
                output=response_data.get('output', '').strip(),
                error=response_data.get('error', '').strip()
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