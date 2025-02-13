from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from models import TestCaseValidationResult

output_parser = PydanticOutputParser(pydantic_object=TestCaseValidationResult)

# System prompt for initial code generation
SYSTEM_PROMPT = PromptTemplate(
    input_variables=["language", "question", "test_cases", "explanation"],
    template=(
        "You are an expert software engineer. Before writing the code, break down the problem into smaller steps and think through the solution.\n\n"
        "### Problem:\n{question}\n\n"
        "### Test Cases:\n{test_cases}\n\n"
        "### Explanation:\n{explanation}\n\n"
        "### Instructions:\n"
        "1. **Think through the problem**: Break down the problem into smaller steps and outline the solution.\n"
        "2. **Write clean, efficient, and correct {language} code** that handles all edge cases.\n"
        "3. Include comments and docstrings for clarity.\n"
        "4. Print only the code without any additional explanations or text.\n"
        "5. Do not include any test cases or example usage in the code.\n"
        "6. Ensure the code prints the output from the input passed, as it will be sent to a compiler for validation.\n"
    )
)

# Refinement prompt for fixing errors
# In the prompts.py file, update the REFINE_PROMPT
REFINE_PROMPT = PromptTemplate(
    input_variables=["language", "question" , "code", "results", "error", "test_cases"],
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