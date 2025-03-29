from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TestCaseResult(BaseModel):
    input: str = Field(description="Input for the test case")
    expected_output: Optional[str] = Field(description="Expected output for the test case")
    actual_output: Optional[str] = Field(description="Actual output from the code execution")
    stderror: Optional[str] = Field(description="The error message if a runtime error occurred during execution")
    compiler_errors: Optional[str] = Field(description="The compiler errors if any occurred during compilation")
    time: str = Field(description="The time taken for code execution")
    memory: int = Field(description="The memory used during code execution")
    passed: bool = Field(description="Whether the test case passed")

class TestCaseValidationResult(BaseModel):
    test_results: List[TestCaseResult] = Field(description="List of test case validation results")

class TestCase(BaseModel):
    input: str = Field(description="Input for the test case")
    expected_output: Optional[str] = Field(description="Expected output for the test case (can be None for invalid inputs)")

class CodeExecutionResult(BaseModel):
    output: str = Field(description="The output of the code execution")
    time: str = Field(description="The time taken for code execution")
    memory: int = Field(description="The memory used during code execution")
    stderror: str = Field(description="The error message if a runtime error occurred during execution")
    compiler_errors: str = Field(description="The compiler errors if any occurred during compilation")

class CodeIterationHistory(BaseModel):
    iteration: int = Field(description="The iteration number")
    chain_of_thought:  List[str] = Field(description="The chain of thought for this iteration")
    code: str = Field(description="The generated or refined code")
    execution_result: CodeExecutionResult = Field(description="The result of the code execution")
    test_results: List[TestCaseResult] = Field(description="Results of test case validation")

class PipelineResult(BaseModel):
    cot: List[str] = Field(description="The chain of thought as a list of reasoning steps")
    final_code: str = Field(description="The final generated or refined code")
    final_result: CodeExecutionResult = Field(description="The final execution result")
    test_results: List[TestCaseResult] = Field(description="Results of test case validation")
    iterations: int = Field(description="Total number of iterations")
    history: List[CodeIterationHistory] = Field(description="History of all iterations")
    success: bool = Field(description="Whether the pipeline was successful")