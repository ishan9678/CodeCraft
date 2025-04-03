import httpx
import re
import logging
from typing import List, Dict, Any
from models import CodeIterationHistory, PipelineResult, TestCase, TestCaseResult, CodeExecutionResult
from executor import execute_code
from generator import CodeGenerator
import json

logger = logging.getLogger(__name__)

class CodeGenerationPipeline:
    def __init__(self, api_key: str, base_url: str, max_iterations: int = 3):
        self.generator = CodeGenerator(api_key=api_key, base_url=base_url)
        self.max_iterations = max_iterations
    
    def normalize_array_string(self, s: str) -> str:
        """Normalize array string by removing spaces between elements, preserving structure."""
        if not (s.startswith("[") and s.endswith("]")):
            return s
        
        # Use regex to handle nested structures while removing spaces between array elements
        # Preserve spaces inside string literals
        in_string = False
        escape_next = False
        result = []
        
        for char in s:
            if char == '"' or char == "'":
                if not escape_next:
                    in_string = not in_string
            elif char == '\\' and in_string:
                escape_next = True
                result.append(char)
                continue
                
            if char == ' ' and not in_string:
                continue
            
            result.append(char)
            escape_next = False
                
        return ''.join(result)
    
    def parse_llm_response(self, response_text):
        """Parses LLM response to extract chain of thought and formatted code."""
        # Extract Chain of Thought
        thought_start = response_text.find("CHAIN_OF_THOUGHT:")
        code_start = response_text.find("CODE:")

        if thought_start == -1 or code_start == -1:
            raise ValueError("Response format invalid: Missing CHAIN_OF_THOUGHT or CODE section.")

        # Extract and clean Chain of Thought
        chain_of_thought_lines = response_text[thought_start + len("CHAIN_OF_THOUGHT:"):code_start].strip().split("\n")
        chain_of_thought = [line.lstrip("- ").strip() for line in chain_of_thought_lines if line.strip()]

        # Extract Code using regex (captures everything inside triple backticks)
        code_match = re.search(r"```(?:\w+)?\n(.*?)```", response_text, re.DOTALL)
        if not code_match:
            raise ValueError("Response format invalid: No properly formatted code block found.")

        corrected_code = code_match.group(1).strip()

        return chain_of_thought, corrected_code

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
            test_cases_dict = self.generator.generate_test_cases(model, language, question, explanation, user_input)
            test_cases = [TestCase(**test_case) for test_case in test_cases_dict]
        
        while iteration < self.max_iterations:
            try:
                # Generate or refine code
                if current_code is None:
                    # Serialize test cases to dictionaries
                    test_cases_dict = [test_case.dict() for test_case in test_cases]
                    current_code = self.generator.generate_initial_code(model, language, question, test_cases_dict, explanation)
                else:
                    # Serialize test cases to dictionaries before passing to refine_code
                    test_cases_dict = [test_case.dict() for test_case in test_cases]

                try:
                    cot, code = self.parse_llm_response(current_code)
                    print("Extracted Chain of Thought:", cot)
                    print("Extracted Code:\n", code)
                except json.JSONDecodeError as e:
                    print("JSON parsing error:", e)
                except Exception as e:
                    print("Unexpected error:", e)

                # Execute the code with user input (if provided)
                print('the code before execution is:', code)
                execution_result = await execute_code(code, language, user_input)
                
                # Validate test cases
                test_case_results = []
                for test_case in test_cases:
                    test_case_result = await execute_code(code, language, test_case.input)
                    
                    # Enhanced comparison logic
                    actual = test_case_result.output.strip()
                    expected = test_case.expected_output.strip() if test_case.expected_output else ""
                    
                    passed = (
                        actual == expected or 
                        actual.lower() == expected.lower() or
                        self.normalize_array_string(actual) == self.normalize_array_string(expected) or
                        self.normalize_array_string(actual.lower()) == self.normalize_array_string(expected.lower())
                    ) if expected else False
                    
                    test_case_results.append(TestCaseResult(
                        input=test_case.input,
                        expected_output=test_case.expected_output,
                        actual_output=test_case_result.output,
                        passed=passed,
                        stderror=test_case_result.stderror,
                        compiler_errors=test_case_result.compiler_errors,
                        time=test_case_result.time,
                        memory=test_case_result.memory
                    ))
                
                # Pass test case results to the LLM for validation
                # test_results = self.generator.validate_test_cases(model, json.dumps([result.dict() for result in test_case_results]))
                
                # Store iteration history
                history.append(CodeIterationHistory(
                    iteration=iteration + 1,
                    chain_of_thought=cot,
                    code=code,
                    execution_result=execution_result,
                    test_results=test_case_results   
                ))
                
                # Check if all test cases passed
                if all(test_case.passed for test_case in test_case_results):
                    logger.info("All test cases passed. Stopping pipeline.")
                    break
                
                iteration += 1

                current_code = self.generator.refine_code(model, language, question, code, test_cases_dict, test_case_results)
            
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e}")
                history.append(CodeIterationHistory(
                    iteration=iteration + 1,
                    chain_of_thought=cot,
                    code=code,
                    execution_result=CodeExecutionResult(output='', stderror='', time='0', memory='0', compiler_errors=''),
                    test_results=[]
                ))
                break
            except Exception as e:
                logger.error(f"Execution error occurred: {e}")
                history.append(CodeIterationHistory(
                    iteration=iteration + 1,
                    chain_of_thought=cot,
                    code=code,
                    execution_result=CodeExecutionResult(output='', stderror='', time='0', memory='0', compiler_errors=''),
                    test_results=[]
                ))
                break
        
        return PipelineResult(
            cot=cot,
            final_code=code,
            final_result=execution_result,
            test_results=test_case_results,
            iterations=iteration + 1,
            history=history,
            success=all(test_case.passed for test_case in test_case_results)
        )