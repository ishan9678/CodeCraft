import httpx
import logging
from models import CodeExecutionResult, TestCase
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

async def execute_code(code: str, language: str, user_input: str = "") -> CodeExecutionResult:
    """Execute code using the compiler API"""
    url = 'https://api.codex.jaagrav.in'
    payload = {
        'code': code,
        'language': language,
        'input': user_input
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                return CodeExecutionResult(output=response_data.get('output', ''), error=response_data.get('error', ''))
            return CodeExecutionResult(output='', error=f"HTTP Error: {response.status_code}")
        except Exception as e:
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