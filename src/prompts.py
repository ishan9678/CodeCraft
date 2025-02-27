from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from models import TestCaseValidationResult

output_parser = PydanticOutputParser(pydantic_object=TestCaseValidationResult)

# System prompt for initial code generation
SYSTEM_PROMPT = PromptTemplate(
    input_variables=["language", "question", "test_cases", "explanation"],
    template=(
        "You are an expert {language} engineer tasked with solving a coding problem. Your solution will be submitted to the Judge0 API, which will provide inputs dynamically and compare the output against expected test case results. Follow these steps:\n\n"
        "1. Analyze the problem carefully:\n{question}\n\n"
        "2. Review the explanation for clarity:\n{explanation}\n\n"
        "3. Study the sample test cases to understand input-output expectations:\n{test_cases}\n\n"
        "4. Plan your approach:\n"
        " - Break down the problem into clear, logical steps.\n"
        " - Consider edge cases (e.g., empty inputs, large numbers, invalid data) and ensure robustness.\n"
        " - Optimize for efficiency while maintaining readability.\n"
        "5. Implement a solution in {language} that:\n"
        " - Defines a function accepting dynamic inputs as parameters.\n"
        " - Returns or prints the exact output expected by the test cases.\n"
        " - Handles all test cases correctly when executed.\n"
        "6. Validate your solution:\n"
        " - Ensure the function’s output matches the test case outputs precisely (e.g., correct format, no extra spaces).\n"
        " - Test mentally or simulate with the provided test cases.\n"
        "7. Format the response as a valid JSON object with no text outside this structure:\n"
        "{{\n"
        " \"chain_of_thought\": [\n"
        " \"Step 1: [Your first reasoning step]\",\n"
        " \"Step 2: [Your second reasoning step]\",\n"
        " // ... additional steps as needed\n"
        " ],\n"
        " \"code\": \"[Your complete {language} code, including a function definition and a print statement calling the function with generic variables (e.g., print(function_name(a, b)))]\"\n"
        "}}\n\n"
        "8. Specific requirements:\n"
        " - The code must include a function that takes inputs dynamically.\n"
        " - Add a print statement after the function, calling it with generic variables (e.g., print(function_name(a, b))), NOT hardcoded values, so Judge0 can inject test case inputs.\n"
        " - Ensure the output matches the test case expectations exactly for Judge0 API validation.\n"
        " - Use only standard {language} libraries unless specified otherwise.\n"
        " - Assume inputs will be provided by Judge0 in the format implied by the test cases (e.g., space-separated values, newlines).\n\n"
        "Focus on correctness, clarity, and compatibility with Judge0’s dynamic input system."
    )
)

REFINE_PROMPT = PromptTemplate(
    input_variables=["language", "question", "code", "results", "error", "test_cases"],
    template=(
        "You are a highly skilled software engineer. Your task is to refine and debug the given {language} code to "
        "fix errors, improve functionality, and ensure correctness.\n\n"
        
        "### Problem:\n{question}\n\n"

        "### Original Code:\n{code}\n\n"
        
        "### Execution Results:\n{results}\n\n"
        
        "### Error Messages:\n{error}\n\n"
        
        "### Test Cases to Pass:\n{test_cases}\n\n"
        
        "### Refinement Instructions:\n"
        "1. **Analyze** the given errors, execution results, and expected test cases.\n"
        "2. **Think through the solution**: Break down the problem and outline the steps to fix the errors.\n"
        "3. **Fix all syntax and logical errors**, ensuring the code executes without crashing.\n"
        "4. **Pay attention to output formatting**: Ensure the output matches the expected format exactly, including casing\n"
        "5. **Improve efficiency**, readability, and robustness by handling edge cases.\n"
        "6. **Iteratively refine the logic** so that all test cases pass successfully.\n"
        "7. **Do not modify the input/output format**—the code must produce output exactly as expected.\n"
        "8. **Return only the corrected code** without additional explanations or comments.\n"
        "9. **Ensure correctness on every iteration**— fix all the testcases that failed.\n\n"
        
        "Your output should contain only the improved code, nothing else."
    )
)

# Prompt for test case validation
VALIDATE_TEST_CASES_PROMPT = PromptTemplate(
    input_variables=["test_cases"],
    template=(
        "You are an expert software engineer. Validate the following test cases based on the actual outputs from the code execution:\n\n"
        "### Test Cases:\n{test_cases}\n\n"
        "### Instructions:\n"
        "1. Compare the actual output with the expected output for each test case.\n"
        "2. Return the validation results in the following JSON format:\n"
        "3. Do not provide code, your job is just to compare the outputs.\n"
        "4. Just return the validation results without any additional explanations or text.\n"
        "{format_instructions}\n"
    ),
    partial_variables={"format_instructions": output_parser.get_format_instructions()}
)

TEST_CASE_GENERATION_PROMPT = PromptTemplate(
    input_variables=["question", "explanation"],
    template=(
    "You are an expert software engineer. Generate a set of test cases for the following problem:\n\n"
    "### Problem:\n{question}\n\n"
    "### Explanation:\n{explanation}\n\n"
    "### Instructions:\n"
    "1. Generate at least 5 test cases that cover various scenarios, including edge cases.\n"
    "2. For each test case, provide the input and the expected output.\n"
    "3. Return the test cases in JSON format as a list of objects with 'input' and 'expected_output' fields.\n"
    "4. input and expected_output should be strings.\n"
    "5. Do not include any additional explanations or text.\n"
    ),
)