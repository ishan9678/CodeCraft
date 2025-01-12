from openai import OpenAI
from prompts import SYSTEM_PROMPT, REFINE_PROMPT

class CodeGenerator:
    def __init__(self, api_key: str, base_url: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate_response(self, prompt: str) -> str:
        """Generate response using SambaNova API"""
        response = self.client.chat.completions.create(
            model='Meta-Llama-3.3-70B-Instruct',
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            top_p=0.1
        )
        return response.choices[0].message.content

    def generate_initial_code(self, language: str, question: str, test_cases: str, explanation: str) -> str:
        """Generate initial code using the system prompt"""
        prompt = SYSTEM_PROMPT.format(
            language=language,
            question=question,
            test_cases=test_cases,
            explanation=explanation
        )
        return self.generate_response(prompt)

    def refine_code(self, language: str, code: str, results: str, error: str, test_cases: str) -> str:
        """Refine code using the refine prompt"""
        prompt = REFINE_PROMPT.format(
            language=language,
            code=code,
            results=results,
            error=error,
            test_cases=test_cases
        )
        return self.generate_response(prompt)