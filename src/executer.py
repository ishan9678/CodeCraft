import httpx
import logging
from models import CodeExecutionResult

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