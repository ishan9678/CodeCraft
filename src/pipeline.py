import re
import logging
from typing import List, Dict, Any
from models import CodeIterationHistory, PipelineResult, TestCase, TestCaseResult
from executor import execute_code
from generator import CodeGenerator
import json

logger = logging.getLogger(__name__)

class CodeGenerationPipeline:
    def __init__(self, api_key: str, base_url: str, max_iterations: int = 3):
        self.generator = CodeGenerator(api_key=api_key, base_url=base_url)
        self.max_iterations = max_iterations

    def clean_code(self, code: str, language: str) -> str:
        """Remove Markdown formatting from the generated code."""
        escaped_language = re.escape(language)
        code = re.sub(rf'```{escaped_language}\s*', '', code)
        code = re.sub(r'\s*```\s*', '', code)
        return code.strip()

    async def run_pipeline(
        self,
        model: str,
        language: str,
        question: str,
        test_cases: List[TestCase],
        explanation: str,
        user_input: str = "" 
    ) -> PipelineResult:
        """Run the complete code generation and refinement pipeline."""
        iteration = 0
        current_code = None
        history = []
        
        # Generate test cases if none are provided
        if not test_cases:
            test_cases_dict = self.generator.generate_test_cases(model, language, question, explanation)
            test_cases = [TestCase(**test_case) for test_case in test_cases_dict]
        
        while iteration < self.max_iterations:
            # Generate or refine code
            if current_code is None:
                # Serialize test cases to dictionaries
                test_cases_dict = [test_case.dict() for test_case in test_cases]
                current_code = self.generator.generate_initial_code(model, language, question, test_cases_dict, explanation)
            else:
                # Serialize test cases to dictionaries before passing to refine_code
                test_cases_dict = [test_case.dict() for test_case in test_cases]
                current_code = self.generator.refine_code(model, language, current_code, execution_result.output, execution_result.error, test_cases_dict)
            
            # Clean the code
            current_code = self.clean_code(current_code, language=language)
            
            # Execute the code with user input (if provided)
            execution_result = await execute_code(current_code, language, user_input)
            
            # Validate test cases
            test_case_results = []
            for test_case in test_cases:
                test_case_result = await execute_code(current_code, language, test_case.input)
                passed = test_case_result.output.strip() == test_case.expected_output.strip() if test_case.expected_output else False
                test_case_results.append(TestCaseResult(
                    input=test_case.input,
                    expected_output=test_case.expected_output,
                    actual_output=test_case_result.output,
                    passed=passed,
                    error=test_case_result.error
                ))
            
            # Pass test case results to the LLM for validation
            test_results = self.generator.validate_test_cases(model, json.dumps([result.dict() for result in test_case_results]))
            
            # Store iteration history
            history.append(CodeIterationHistory(
                iteration=iteration + 1,
                code=current_code,
                execution_result=execution_result,
                test_results=test_case_results  # Pass the list of TestCaseResult objects
            ))
            
            # Check if all test cases passed
            if all(test_case.passed for test_case in test_case_results):
                logger.info("All test cases passed. Stopping pipeline.")
                break
            
            iteration += 1
        
        return PipelineResult(
            final_code=current_code,
            final_result=execution_result,
            test_results=test_case_results,
            iterations=iteration + 1,
            history=history,
            success=all(test_case.passed for test_case in test_case_results)
        )