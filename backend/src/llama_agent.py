import streamlit as st
import asyncio
import logging
from models import PipelineRequest
from pipeline import CodeGenerationPipeline
from dotenv import load_dotenv
import os
from db import save_question, save_iteration, save_test_case_results
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# api_key = os.getenv("GROQ_API_KEY")
# if not api_key:
#     raise ValueError("GROQ API KEY is not set")

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI() # Initialize FastAPI

cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

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
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-3.2-3b-preview",
    "llama-3.1-70b-versatile",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
]

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
            max_iterations=data.max_iterations,
            question_code=data.question_code,
        )

        pipeline = CodeGenerationPipeline(
            api_key=data.api_key,
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