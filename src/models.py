from pydantic import BaseModel, Field
from typing import List, Dict, Any

class TestCase(BaseModel):
    input: str = Field(description="Input for the test case")
    expected_output: str = Field(description="Expected output for the test case")

class CodeExecutionResult(BaseModel):
    output: str = Field(description="The output of the code execution")
    error: str = Field(description="Any error messages from the execution")

class CodeIterationHistory(BaseModel):
    iteration: int = Field(description="The iteration number")
    code: str = Field(description="The generated or refined code")
    execution_result: CodeExecutionResult = Field(description="The result of the code execution")
    test_results: List[Dict[str, Any]] = Field(description="Results of test case validation")

class PipelineResult(BaseModel):
    final_code: str = Field(description="The final generated or refined code")
    final_result: CodeExecutionResult = Field(description="The final execution result")
    test_results: List[Dict[str, Any]] = Field(description="Results of test case validation")
    iterations: int = Field(description="Total number of iterations")
    history: List[CodeIterationHistory] = Field(description="History of all iterations")
    success: bool = Field(description="Whether the pipeline was successful")