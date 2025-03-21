import streamlit as st
import asyncio
import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from models import TestCase
from pipeline import CodeGenerationPipeline
from dotenv import load_dotenv
import os
from db import save_question, save_iteration, save_test_case_results
import uvicorn
from fastapi import FastAPI, HTTPException

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ API KEY is not set")

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI() # Initialize FastAPI

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


class PipelineRequest(BaseModel):
    model: str
    language: str
    question: str
    explanation: Optional[str] = None
    user_input: Optional[str] = None
    max_iterations: int = 3
    generate_test_cases: bool = True
    test_cases: Optional[List[TestCase]] = []

@app.post("/run_pipeline")
async def run_pipeline(data: PipelineRequest):
    try:
        # Validate model selection
        if data.model not in model_ids:
            raise HTTPException(status_code=400, detail="Invalid model selected")

        # Validate language selection
        if data.language not in LANGUAGE_MAPPING.values():
            raise HTTPException(status_code=400, detail="Invalid programming language")

        # Save the question in the database
        question = save_question(
            model=data.model,
            question_text=data.question,
            explanation=data.explanation,
            user_input=data.user_input,
            language=data.language,
            max_iterations=data.max_iterations
        )

        pipeline = CodeGenerationPipeline(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            max_iterations=data.max_iterations
        )

        # Run the pipeline
        result = await pipeline.run_pipeline(
            model=data.model,
            language=data.language,
            question=data.question,
            test_cases=data.test_cases,
            explanation=data.explanation,
            user_input=data.user_input
        )

        # Save Iteration History in DB
        for history in result.history:
            iteration = save_iteration(
                question_id=question.id,
                iteration_number=history.iteration,
                chain_of_thought=history.chain_of_thought,
                generated_code=history.code,
                success=all(test_case.passed for test_case in history.test_results)
            )

            # Save Test Case Results for each iteration
            for test_result in history.test_results:
                save_test_case_results(
                    iteration_id=iteration.id,
                    input_data=test_result.input,
                    expected_output=test_result.expected_output,
                    actual_output=test_result.actual_output,
                    execution_time=test_result.time,
                    memory_usage=test_result.memory,
                    stderror=test_result.stderror or "",
                    compiler_errors=test_result.compiler_errors or "",
                    passed=test_result.passed
                )

        return {"success": True, "message": "Pipeline executed successfully", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


# st.title("CodeCraft")

# selected_model = st.selectbox(
#     'Select a model:',
#     model_ids
# )

# # Main input fields
# question = st.text_area(
#     "Question",
#     placeholder="Write a function that returns the sum of two numbers",
#     help="Enter the coding question or task."
# )

# explanation = st.text_area(
#     "Explanation",
#     placeholder="Create a simple function that takes two numbers as input and returns their sum.",
#     help="Provide additional context or explanation."
# )

# user_input = st.text_input(
#     "User Input (for testing)",
#     placeholder="2 3",
#     help="Input to test the generated code."
# )


# # Language dropdown
# language = st.selectbox("Language", list(LANGUAGE_MAPPING.keys()), help="Select the programming language for the code.")
# language_code = LANGUAGE_MAPPING[language]

# # Slider for max iterations
# max_iterations = st.slider("Max Iterations", min_value=1, max_value=5, value=3, help="Maximum number of iterations for the pipeline.")

# # Test cases input
# st.header("Test Cases")

# # Option to generate test cases automatically
# generate_test_cases = st.checkbox("Generate Test Cases Automatically", value=True, help="Automatically generate test cases based on the problem statement.")

# # Initialize session state to store test cases
# if "test_cases" not in st.session_state:
#     st.session_state.test_cases = [{"input": "", "expected_output": ""}]  # Start with one test case

# # Function to add a new test case
# def add_test_case():
#     st.session_state.test_cases.append({"input": "", "expected_output": ""})

# # Collapsible section for test cases
# with st.expander("Manage Test Cases", expanded=True):
#     if not generate_test_cases:
#         # Display test cases
#         test_cases = []
#         for i, test_case in enumerate(st.session_state.test_cases):
#             st.subheader(f"Test Case {i + 1}")
#             input_data = st.text_input(f"Input {i + 1}", value=test_case["input"], key=f"input_{i}", help="Input for the test case.")
#             expected_output = st.text_input(f"Expected Output {i + 1}", value=test_case["expected_output"], key=f"expected_output_{i}", help="Expected output for the test case.")
#             test_cases.append(TestCase(input=input_data, expected_output=expected_output))

#         # Button to add more test cases
#         st.button("Add Test Case", on_click=add_test_case)
#     else:
#         test_cases = []

# # Run pipeline button
# if st.button("Run Pipeline"):
#     pipeline = CodeGenerationPipeline(
#         api_key=api_key,
#         base_url="https://api.groq.com/openai/v1",
#         max_iterations=max_iterations
#     )

#     # Run the pipeline asynchronously
#     async def run_pipeline_async():
#         return await pipeline.run_pipeline(
#             model = selected_model,
#             language=language_code,
#             question=question,
#             test_cases=test_cases,
#             explanation=explanation,
#             user_input=user_input
#         )

#     # Display a spinner while the pipeline is running
#     with st.spinner("Running pipeline..."):
#         # Save the question to the database
#         question = save_question(
#             model=selected_model,
#             question_text=question,
#             explanation=explanation,
#             user_input=user_input,
#             language=language_code,
#             max_iterations=max_iterations
#         )
#         result = asyncio.run(run_pipeline_async())

#     # Display results
#     st.header("Results")
#     st.subheader("Chain of Thought")
#     for i, step in enumerate(result.cot, 1):
#         st.write(f"{i}. {step}")
#     st.subheader("Final Code")
#     st.code(result.final_code, language=language_code)

#     st.subheader("Execution Result")
#     st.text(result.final_result.output)

#     st.subheader("Test Case Results")
#     for i, test_result in enumerate(result.test_results):
#         st.write(f"### Test Case {i + 1}")
#         st.write(f"**Input:** {test_result.input}")  # Use dot notation
#         st.write(f"**Expected Output:** {test_result.expected_output}")  # Use dot notation
#         st.write(f"**Actual Output:** {test_result.actual_output}")  # Use dot notation
#         st.write(f"**Time:** {test_result.time}")  # Use dot notation
#         st.write(f"**Memory:** {test_result.memory}")  # Use dot notation
#         if test_result.stderror:  # Use dot notation
#             st.write(f"**Standard Error:** {test_result.stderror}")  # Use dot notation
#         if test_result.compiler_errors:
#             st.write(f"**Compiler Errors:** {test_case.compiler_errors}")
#         st.write("---")

#     st.subheader("Pipeline Metadata")
#     st.write(f"**Total Iterations:** {result.iterations}")
#     st.write(f"**Success:** {result.success}")

#     # Display iteration history
#     st.subheader("Iteration History")
#     for history in result.history:
#         # Save the iteration to the database
#         iteration = save_iteration(
#             question_id=question.id,
#             iteration_number=history.iteration,
#             chain_of_thought=history.chain_of_thought,
#             generated_code=history.code,
#             success=all(test_case.passed for test_case in history.test_results)
#         )
#         st.write(f"### Iteration {history.iteration}")
#         st.write("**Chain of Thought:**")
#         for i, step in enumerate(history.chain_of_thought, 1):
#             st.write(f"{i}. {step}")
#         st.write("**Generated Code:**")
#         st.code(history.code, language=language_code)
#         st.write("**Execution Result:**")
#         st.text(history.execution_result.output)
#         if history.execution_result.stderror:
#             st.write(f"**Standard Error:** {history.execution_result.stderror}")
#         if history.execution_result.compiler_errors:
#             st.write(f"**Compiler Errors:** {history.execution_result.compiler_errors}")
#         st.write("**Test Case Results:**")
#         for i, test_result in enumerate(history.test_results):
#             save_test_case_results(
#                 iteration_id=iteration.id,
#                 input_data=test_result.input,
#                 expected_output=test_result.expected_output,
#                 actual_output=test_result.actual_output,
#                 execution_time=test_result.time,
#                 memory_usage=test_result.memory,
#                 stderror=test_result.stderror or "",
#                 compiler_errors=test_result.compiler_errors or "",
#                 passed=test_result.passed
#             )
#             st.write(f"#### Test Case {i + 1}")
#             st.write(f"**Input:** {test_result.input}")
#             st.write(f"**Expected Output:** {test_result.expected_output}")
#             st.write(f"**Actual Output:** {test_result.actual_output}")
#             st.write(f"**Time:** {test_result.time}")
#             st.write(f"**Memory:** {test_result.memory}")
#             st.write(f"**Passed:** {test_result.passed}")
#             if test_result.stderror:
#                 st.write(f"**Standard Error:** {test_result.stderror}")
#             if test_result.compiler_errors:
#                 st.write(f"**Compiler Errors:** {test_result.compiler_errors}")
#         st.write("---")