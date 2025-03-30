from db_models import Base, engine, SessionLocal, Question, Iteration, TestCaseResult
from sqlalchemy.orm import Session
import uuid
import datetime

def save_question(model, question_text, explanation, user_input, language, max_iterations, question_code=None):
    session = SessionLocal()
    try:
        question = Question(
            id=uuid.uuid4(),
            model=model,
            question=question_text,
            explanation=explanation,
            user_input=user_input,
            language=language,
            max_iterations=max_iterations,
            question_code=question_code,
            created_at=datetime.datetime.now().isoformat()
        )
        session.add(question)
        session.commit()
        session.refresh(question)  # Get the generated UUID
        return question
    finally:
        session.close()


def save_iteration(question_id, iteration_number, chain_of_thought, generated_code, success):
    session = SessionLocal()
    try:
        iteration = Iteration(
            id=uuid.uuid4(),
            question_id=question_id,
            iteration_number=iteration_number,
            chain_of_thought=chain_of_thought,
            generated_code=generated_code,
            success=success
        )
        session.add(iteration)
        session.commit()
        session.refresh(iteration)
        return iteration
    finally:
        session.close()

def save_test_case_results(iteration_id, input_data, expected_output, actual_output, execution_time, memory_usage, stderror, compiler_errors, passed):
    session = SessionLocal()
    try:
        test_case_result = TestCaseResult(
            id=uuid.uuid4(),
            iteration_id=iteration_id,
            input=input_data,
            expected_output=expected_output,
            actual_output=actual_output,
            execution_time=execution_time,
            memory_usage=memory_usage,
            stderror=stderror,
            compiler_errors=compiler_errors,
            passed=passed
        )
        session.add(test_case_result)
        session.commit()
    finally:
        session.close()