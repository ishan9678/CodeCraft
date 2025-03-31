import httpx
import logging
from models import CodeExecutionResult, TestCase
from typing import List, Dict, Any
from dotenv import load_dotenv
import os
import json

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
            
         
            stderr = response_data.get('stderr', '') or ''
            stdout = response_data.get('stdout', '') or ''
            time = response_data.get('time', '0')
            memory = response_data.get('memory', '0')
            compiler_errors = response_data.get('compile_output', '') or ''
            
            return CodeExecutionResult(
                output=stdout,
                stderror=stderr,
                time=time,
                memory=memory,
                compiler_errors=compiler_errors
            )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
        return CodeExecutionResult(output='', stderror='', time='0', memory='0', compiler_errors='')

    except Exception as e:
        logger.error(f"Execution error occurred: {e}")
        return CodeExecutionResult(output='', stderror='', time='0', memory='0', compiler_errors='')

async def validate_test_cases(code: str, language: str, test_cases: List[TestCase]) -> List[Dict[str, Any]]:
    """Validate the code against all test cases"""
    test_results = []
    for test_case in test_cases:
        execution_result = await execute_code(code, language, test_case.input)

        expected_output = test_case.expected_output.strip()
        actual_output = execution_result.output.strip()

        # Try parsing as JSON (lists, dicts) to compare structured data correctly
        try:
            expected_json = json.loads(expected_output)
            actual_json = json.loads(actual_output)
            passed = expected_json == actual_json  # Compare as parsed JSON
        except json.JSONDecodeError:
            # If not JSON, compare as normalized strings
            passed = " ".join(actual_output.split()) == " ".join(expected_output.split())

        test_results.append({
            "input": test_case.input,
            "expected_output": test_case.expected_output,
            "actual_output": execution_result.output,
            "passed": passed,
            "stderror": execution_result.stderror,
            "compiler_errors": execution_result.compiler_errors,
            "time": execution_result.time,
            "memory": execution_result.memory
        })
    return test_results