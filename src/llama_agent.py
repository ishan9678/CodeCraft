import streamlit as st
import asyncio
import logging
from models import TestCase
from pipeline import CodeGenerationPipeline
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ API KEY is not set")

# Configure logging
logging.basicConfig(level=logging.INFO)

LANGUAGE_MAPPING = {
    "Python": "python",
    "Javascript": "javascript",
    "C++": "cpp",
    "C": "c",
    "Java": "java",
    "Ruby": "ruby",
    "Rust": "rust",
    "R": "r",
    "Go": "go",
    "Swift": "swift",
    "Typescript": "typescript",
    "PHP": "php",
}

model_ids = [
    "llama-3.3-70b-specdec",
    "llama-3.1-8b-instant",
    "llama-3.2-3b-preview",
    "llama-3.1-70b-versatile",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
]

st.title("CodeCraft")

selected_model = st.selectbox(
    'Select a model:',
    model_ids
)

# Main input fields
question = st.text_area(
    "Question",
    placeholder="Write a function that returns the sum of two numbers",
    help="Enter the coding question or task."
)

explanation = st.text_area(
    "Explanation",
    placeholder="Create a simple function that takes two numbers as input and returns their sum.",
    help="Provide additional context or explanation."
)

user_input = st.text_input(
    "User Input (for testing)",
    placeholder="2 3",
    help="Input to test the generated code."
)


# Language dropdown
language = st.selectbox("Language", list(LANGUAGE_MAPPING.keys()), help="Select the programming language for the code.")
language_code = LANGUAGE_MAPPING[language]

# Slider for max iterations
max_iterations = st.slider("Max Iterations", min_value=1, max_value=5, value=3, help="Maximum number of iterations for the pipeline.")

# Test cases input
st.header("Test Cases")

# Option to generate test cases automatically
generate_test_cases = st.checkbox("Generate Test Cases Automatically", value=True, help="Automatically generate test cases based on the problem statement.")

# Initialize session state to store test cases
if "test_cases" not in st.session_state:
    st.session_state.test_cases = [{"input": "", "expected_output": ""}]  # Start with one test case

# Function to add a new test case
def add_test_case():
    st.session_state.test_cases.append({"input": "", "expected_output": ""})

# Collapsible section for test cases
with st.expander("Manage Test Cases", expanded=True):
    if not generate_test_cases:
        # Display test cases
        test_cases = []
        for i, test_case in enumerate(st.session_state.test_cases):
            st.subheader(f"Test Case {i + 1}")
            input_data = st.text_input(f"Input {i + 1}", value=test_case["input"], key=f"input_{i}", help="Input for the test case.")
            expected_output = st.text_input(f"Expected Output {i + 1}", value=test_case["expected_output"], key=f"expected_output_{i}", help="Expected output for the test case.")
            test_cases.append(TestCase(input=input_data, expected_output=expected_output))

        # Button to add more test cases
        st.button("Add Test Case", on_click=add_test_case)
    else:
        test_cases = []

# Run pipeline button
if st.button("Run Pipeline"):
    pipeline = CodeGenerationPipeline(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        max_iterations=max_iterations
    )

    # Run the pipeline asynchronously
    async def run_pipeline_async():
        return await pipeline.run_pipeline(
            model = selected_model,
            language=language_code,
            question=question,
            test_cases=test_cases,
            explanation=explanation,
            user_input=user_input
        )

    # Display a spinner while the pipeline is running
    with st.spinner("Running pipeline..."):
        result = asyncio.run(run_pipeline_async())

    # Display results
    st.header("Results")
    st.subheader("Chain of Thought")
    for i, step in enumerate(result.cot, 1):
        st.write(f"{i}. {step}")
    st.subheader("Final Code")
    st.code(result.final_code, language=language_code)

    st.subheader("Execution Result")
    st.text(result.final_result.output)

    st.subheader("Test Case Results")
    for i, test_result in enumerate(result.test_results):
        st.write(f"### Test Case {i + 1}")
        st.write(f"**Input:** {test_result.input}")  # Use dot notation
        st.write(f"**Expected Output:** {test_result.expected_output}")  # Use dot notation
        st.write(f"**Actual Output:** {test_result.actual_output}")  # Use dot notation
        st.write(f"**Passed:** {test_result.passed}")  # Use dot notation
        if test_result.error:  # Use dot notation
            st.write(f"**Error:** {test_result.error}")
        st.write("---")

    st.subheader("Pipeline Metadata")
    st.write(f"**Total Iterations:** {result.iterations}")
    st.write(f"**Success:** {result.success}")

    # Display iteration history
    st.subheader("Iteration History")
    for history in result.history:
        st.write(f"### Iteration {history.iteration}")
        st.write("**Chain of Thought:**")
        for i, step in enumerate(history.chain_of_thought, 1):
            st.write(f"{i}. {step}")
        st.write("**Generated Code:**")
        st.code(history.code, language=language_code)
        st.write("**Execution Result:**")
        st.text(history.execution_result.output)
        if history.execution_result.error:
            st.write(f"**Error:** {history.execution_result.error}")
        st.write("**Test Case Results:**")
        for i, test_result in enumerate(history.test_results):
            st.write(f"#### Test Case {i + 1}")
            st.write(f"**Input:** {test_result.input}")
            st.write(f"**Expected Output:** {test_result.expected_output}")
            st.write(f"**Actual Output:** {test_result.actual_output}")
            st.write(f"**Passed:** {test_result.passed}")
            if test_result.error:
                st.write(f"**Error:** {test_result.error}")
        st.write("---")