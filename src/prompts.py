from langchain.prompts import PromptTemplate

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
        "3. Return **only the code** without any additional explanations or text.\n"
        "4. Make sure the code passes all provided test cases.\n"
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
        "4. Return **only the fixed code** without any additional explanations or text.\n"
    )
)