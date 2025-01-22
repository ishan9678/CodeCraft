import httpx
import logging
from models import CodeExecutionResult, TestCase
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()

api_url = os.getenv('COMPILER_API_ENDPOINT')

logger = logging.getLogger(__name__)

LANGUAGE_IDS = {
    "python": 71,
    "cpp": 54,
    "c": 50,
    "javascript": 63,
    "java": 62,
    "ruby": 72,
    "rust": 73,
    "r": 80,
    "go": 60,
    "swift": 83,
    "typescript": 74,
    "php": 68,
}

async def execute_code(code: str, language: str, input: str) -> CodeExecutionResult:
    """
    Execute the code using the Judge0 API.
    """
    url = f"{api_url}/submissions/?base64_encoded=false&wait=true"

    language_id = LANGUAGE_IDS.get(language.lower())
    if not language_id:
        raise ValueError(f"Unsupported language: {language}")
    
    payload = {
        'source_code': code,
        'language_id': language_id,
        'stdin': input
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30)
            response.raise_for_status()  # Raise HTTP errors
            response_data = response.json()
            logger.info(f"Response data: {response_data}")
            
            # Handle stderr which can be null or a string
            stderr = response_data['stderr'] if response_data['stderr'] is not None else ''
            
            return CodeExecutionResult(
                output=response_data['stdout'],
                error=stderr
            )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
        return CodeExecutionResult(output='', error=f"HTTP error: {e}")  
    except Exception as e:
        logger.error(f"Execution error occurred: {e}")
        return CodeExecutionResult(output='', error=f"Execution error: {e}")

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