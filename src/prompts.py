from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from models import TestCaseValidationResult

output_parser = PydanticOutputParser(pydantic_object=TestCaseValidationResult)

# System prompt for initial code generation
SYSTEM_PROMPT = PromptTemplate(
    input_variables=["language", "question", "test_cases", "explanation"],
    template=(
        "You are an expert software engineer. Write clean, efficient, and correct {language} code for the following problem:\n\n"
        "### Problem:\n{question}\n\n"
        "### Test Cases:\n{test_cases}\n\n"
        "### Explanation:\n{explanation}\n\n"
        "### Instructions:\n"
        "1. Ensure the code is syntactically correct and handles all edge cases.\n"
        "2. Include comments and docstrings for clarity.\n"
        "3. Print only the code without any additional explanations or text.\n"
        "4. Do not include any test cases or example usage in the code.\n"
        "5. Do not print the expected outputs or test cases, only print the output.\n"
        "6. Ensure the code prints the output from the input passed, as it will be sent to a compiler for validation.\n"
    )
)

# Refinement prompt for fixing errors
REFINE_PROMPT = PromptTemplate(
    input_variables=["language", "code", "results", "error", "test_cases"],
    template=(
        "You are an expert software engineer. Refine the following {language} code to fix errors and improve functionality:\n\n"
        "### Original Code:\n{code}\n\n"
        "### Execution Results:\n{results}\n\n"
        "### Error Messages:\n{error}\n\n"
        "### Test Cases to Pass:\n{test_cases}\n\n"
        "### Instructions:\n"
        "1. Analyze the errors and execution results carefully.\n"
        "2. Fix any syntax errors, logical errors, or edge cases.\n"
        "3. Ensure the refined code passes all provided test cases.\n"
        "4. Return only the fixed code without any additional explanations or text.\n"
        "5. Do not include any test cases or example usage in the code.\n"
        "6. Ensure the code prints the output from the input passed, as it will be sent to a compiler for validation.\n"
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