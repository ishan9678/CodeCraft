import json
from openai import OpenAI
from typing import List, Dict, Any
from prompts import SYSTEM_PROMPT, REFINE_PROMPT, VALIDATE_TEST_CASES_PROMPT
from langchain.output_parsers import PydanticOutputParser
from models import TestCaseValidationResult
import logging
import re

logger = logging.getLogger(__name__)

class CodeGenerator:
    def __init__(self, api_key: str, base_url: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.output_parser = PydanticOutputParser(pydantic_object=TestCaseValidationResult)

    def generate_response(self, prompt: str, model: str) -> str:
        """Generate response using groq API."""
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            top_p=0.1
        )
        return response.choices[0].message.content

    def generate_initial_code(self, model:str, language: str, question: str, test_cases: List[Dict[str, Any]], explanation: str) -> str:
        """Generate initial code that reads JSON input."""
        prompt = SYSTEM_PROMPT.format(
            language=language,
            question=question,
            test_cases=json.dumps(test_cases),  # Serialize test cases to JSON
            explanation=explanation
        )
        return self.generate_response(prompt, model)

    def refine_code(self, model:str, language: str, code: str, results: str, error: str, test_cases: List[Dict[str, Any]]) -> str:
        prompt = REFINE_PROMPT.format(
            language=language,
            code=code,
            results=results,
            error=error,
            test_cases=json.dumps(test_cases)  # Serialize test cases to JSON
        )
        return self.generate_response(prompt, model)

    def validate_test_cases(self, model:str, test_cases: str) -> TestCaseValidationResult:
        """Validate test cases using the LLM."""
        prompt = VALIDATE_TEST_CASES_PROMPT.format(test_cases=test_cases)
        response = self.generate_response(prompt, model)
        
        # Clean the response to remove unnecessary markdown or other noise
        clean_response = re.sub(r'```(json)?\s*', '', response)
        clean_response = re.sub(r'\s*```\s*', '', clean_response)

        try:
            return self.output_parser.parse(clean_response)
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise ValueError("Failed to parse LLM response as JSON.")