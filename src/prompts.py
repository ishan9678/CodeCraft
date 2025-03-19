from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from models import TestCaseValidationResult

output_parser = PydanticOutputParser(pydantic_object=TestCaseValidationResult)

# System prompt for initial code generation
SYSTEM_PROMPT = PromptTemplate(
    input_variables=["language", "question", "test_cases", "explanation"],
    template=(
        "You are an expert {language} engineer tasked with solving a coding problem. "
        "Your solution will be submitted to the Judge0 API, which will provide inputs dynamically through standard input (stdin) "
        "and compare the output against expected test case results. Follow these steps carefully:\n\n"

        "1. **Analyze the problem carefully:**\n{question}\n\n"

        "2. **Review the explanation for clarity:**\n{explanation}\n\n"

        "3. **Study the sample test cases to understand input-output expectations:**\n{test_cases}\n\n"

        "4. **Plan your approach:**\n"
        "   - Break down the problem into clear, logical steps.\n"
        "   - Consider edge cases (e.g., empty inputs, large numbers, invalid data) and ensure robustness.\n"
        "   - Optimize for efficiency while maintaining readability.\n\n"

        "5. **Implement a solution in {language} that:**\n"
        "   - MUST read input from standard input (stdin) using the appropriate method for {language}.\n"
        "   - Processes the input correctly, converting data types as needed.\n"
        "   - MUST print the exact output to standard output (stdout) as expected by the test cases.\n\n"

        "6. **Validate your solution:**\n"
        "   - Ensure the output matches the expected test case outputs exactly (correct format, no extra spaces).\n"
        "   - Test mentally or simulate with the provided test cases.\n\n"

        "7. **Format your response in the following YAML-style format with clear section markers:**\n"
            "```\n"
            "CHAIN_OF_THOUGHT:\n"
            "- Step 1: [Your first reasoning step]\n"
            "- Step 2: [Your second reasoning step]\n"
            "# Add as many steps as needed\n"
            "\n"
            "CODE:\n"
            "[Your full solution code with appropriate stdin handling for {language}]\n"
            "```\n\n"

        "8. **Strict requirements for Judge0 compatibility:**\n"
        "   - The code MUST read ALL input from standard input (stdin) using the appropriate method for {language}.\n"
        "     * Python: Use `sys.stdin.read()` or `input()`\n"
        "     * Java: Use `Scanner` with `System.in`\n"
        "     * C++: Use `cin`, `getline()`, or other stdin methods\n"
        "     * JavaScript: Use `process.stdin` methods\n"
        "     * Other languages: Use their standard input reading mechanism\n"
        "   - The code MUST write ALL output to standard output (stdout) using appropriate printing methods.\n"
        "   - Do NOT expect interactive user prompts; Judge0 provides all input at once via stdin.\n"
        "   - The solution must NOT contain hardcoded test values; it must process input dynamically.\n"
        "   - Use only standard libraries for {language} unless specified otherwise.\n\n"

        "Focus on correctness, exact output formatting, and compatibility with Judge0's stdin/stdout system."
    )
)

REFINE_PROMPT = PromptTemplate(
    input_variables=["language", "question", "code", "test_cases", "test_case_results"],
    template=(
        "You are an expert {language} engineer tasked with debugging and refining code that failed to pass all test cases. "
        "Your solution will be submitted to the Judge0 API, which will provide inputs dynamically through standard input (stdin) "
        "and compare the output against expected test case results. Follow these steps carefully:\n\n"

        "1. **Analyze the original problem:**\n{question}\n\n"

        "2. **Review the original code that needs fixing:**\n{code}\n\n"

        "3. **Study the test case results:**\n"
        "   Test Case Results:\n{test_case_results}\n\n"
        "   Pay special attention to the actual outputs and compare them with the expected outputs.\n"
        "   Identify the specific test cases that failed and the reasons for the failures.\n\n"
        "   **Note:** If the actual output is correct but fails due to formatting, consider updating the expected output.\n\n"

        "4. **Review the test cases that need to pass:**\n{test_cases}\n\n"

        "5. **Debug and refine the approach:**\n"
        "   - Identify the root causes of failures or errors.\n"
        "   - Pay special attention to input/output errors that occur when reading from stdin.\n"
        "   - Implement robust error handling for all input operations.\n"
        "   - Ensure the solution correctly handles all edge cases, including:\n"
        "     * Empty inputs\n"
        "     * Whitespace-only inputs\n"
        "     * Unexpected input formats\n"
        "     * End-of-file conditions\n"
        "   - Fix all syntax errors, logical errors, and edge case handling.\n"
        "   - Maintain or improve code efficiency and readability.\n\n"

        "6. **Implement the corrected solution in {language} that:**\n"
        "   - MUST read input from standard input (stdin) using the appropriate method for {language}.\n"
        "   - MUST include proper error handling for all input operations.\n"
        "   - Processes the input correctly, converting data types as needed.\n"
        "   - MUST print the exact output to standard output (stdout) as expected by the test cases.\n\n"

        "7. **Validate your solution:**\n"
        "   - Ensure the output matches the expected test case outputs exactly (correct format, no extra spaces).\n"
        "   - Verify that all edge cases are handled correctly.\n"
        "   - Test mentally or simulate with the provided test cases.\n\n"

        "8. **Format your response in the following YAML-style format with clear section markers:**\n"
            "```\n"
            "CHAIN_OF_THOUGHT:\n"
            "- Step 1: [Your first reasoning step]\n"
            "- Step 2: [Your second reasoning step]\n"
            "# Add as many steps as needed\n"
            "\n"
            "CODE:\n"
            "[Your fully corrected solution code]\n"
            "```\n\n"

        "9. **Strict requirements for Judge0 compatibility:**\n"
        "   - The code MUST read ALL input from standard input (stdin) using the appropriate method for {language}.\n"
        "   - The code MUST implement proper error handling for all input operations.\n"
        "   - The code MUST write ALL output to standard output (stdout) using appropriate printing methods.\n"
        "   - Do NOT expect interactive user prompts; Judge0 provides all input at once via stdin.\n"
        "   - The solution must NOT contain hardcoded test values; it must process input dynamically.\n"
        "   - The `code` field in JSON must be a **single-line string** with escaped newlines for proper formatting.\n"
        "   - Use only standard libraries for {language} unless specified otherwise.\n\n"

        "Focus on fixing the specific issues while maintaining compatibility with Judge0's stdin/stdout system."
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
        "4. If output difference is just in casing or whitespace mark it as passed.\n"
        "5. Just return the validation results without any additional explanations or text.\n"
        "{format_instructions}\n"
    ),
    partial_variables={"format_instructions": output_parser.get_format_instructions()}
)

TEST_CASE_GENERATION_PROMPT = PromptTemplate(
    input_variables=["question", "explanation", "example_input"],
    template=(
        "You are an expert software engineer. Generate test cases for this problem:\n\n"
        "### Problem:\n{question}\n\n"
        "### Explanation:\n{explanation}\n\n"
        "### Example Test Case Format:\n{example_input}\n\n"
        "### Instructions:\n"
        "1. Generate 5 test cases covering normal, edge, and corner cases\n"
        "2. Maintain EXACTLY the same input/output format and data types as the example\n"
        "3. For array inputs, match the exact string representation (commas, brackets, quotes)\n"
        "4. Do not include any empty input test cases\n"
        "5. Return JSON list of objects with 'input' and 'expected_output' string fields\n"
        "6. No additional text or explanations - only valid JSON\n"
        "\nEnsure:\n"
        "- Input formatting matches the example's structure and syntax precisely\n"
        "- Output values are computed correctly for given inputs\n"
        "- All string values use same quoting style as example\n"
        "- Numerical precision matches example's decimal places\n"
        "6. Output MUST be ONLY the JSON array with no surrounding text\n"
        "7. Ensure valid JSON syntax - proper commas, quotes, and brackets\n"
        "8. Never include test case explanations or commentary\n"
        "9. Response must start with '[' and end with ']'\n"
        "10. Format exactly like this example:\n{example_input}"
    ),
)
