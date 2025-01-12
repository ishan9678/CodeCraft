import re
import logging
from typing import Optional, Dict, Any, List
from models import CodeExecutionResult, CodeIterationHistory, PipelineResult
from executor import execute_code
from generator import CodeGenerator
from prompts import SYSTEM_PROMPT, REFINE_PROMPT

logger = logging.getLogger(__name__)

class CodeGenerationPipeline:
    def __init__(self, api_key: str, base_url: str, max_iterations: int = 3):
        self.generator = CodeGenerator(api_key=api_key, base_url=base_url)
        self.max_iterations = max_iterations

    def clean_code(self, code: str) -> str:
        """Remove Markdown formatting from the generated code."""
        code = re.sub(r'```(python)?\s*', '', code)
        code = re.sub(r'\s*```\s*', '', code)
        return code.strip()

    async def run_pipeline(
        self,
        language: str,
        question: str,
        test_cases: str,
        explanation: str,
        user_input: str = ""
    ) -> PipelineResult:
        """Run the complete code generation and refinement pipeline."""
        iteration = 0
        current_code = None
        history = []
        
        while iteration < self.max_iterations:
            # Generate or refine code
            if current_code is None:
                current_code = self.generator.generate_initial_code(language, question, test_cases, explanation)
            else:
                current_code = self.generator.refine_code(language, current_code, execution_result.output, execution_result.error, test_cases)
            
            # Clean the code
            current_code = self.clean_code(current_code)
            
            # Execute the code
            execution_result = await execute_code(current_code, language, user_input)
            
            # Store iteration history
            history.append(CodeIterationHistory(
                iteration=iteration + 1,
                code=current_code,
                execution_result=execution_result
            ))
            
            # Check if code execution was successful
            if not execution_result.error and execution_result.output:
                logger.info("Code executed successfully. Stopping pipeline.")
                break
            
            iteration += 1
        
        return PipelineResult(
            final_code=current_code,
            final_result=execution_result,
            iterations=iteration + 1,
            history=history,
            success=not execution_result.error and execution_result.output != ""
        )