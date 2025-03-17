from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set.")

# Create database engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class for models
Base = declarative_base()

# Question Model
class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model = Column(String(255))
    question = Column(Text)
    explanation = Column(Text)
    user_input = Column(String(255))
    language = Column(String(50))
    max_iterations = Column(Integer)

    iterations = relationship("Iteration", back_populates="question", cascade="all, delete-orphan")

# Iteration Model
class Iteration(Base):
    __tablename__ = "iterations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"))
    iteration_number = Column(Integer)
    chain_of_thought = Column(Text)
    generated_code = Column(Text)
    success = Column(Boolean)

    question = relationship("Question", back_populates="iterations")
    test_cases = relationship("TestCaseResult", back_populates="iteration", cascade="all, delete-orphan")

# Test Case Result Model
class TestCaseResult(Base):
    __tablename__ = "test_case_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    iteration_id = Column(UUID(as_uuid=True), ForeignKey("iterations.id", ondelete="CASCADE"))
    input = Column(Text)
    expected_output = Column(Text)
    actual_output = Column(Text)
    execution_time = Column(Float)
    memory_usage = Column(Integer)
    stderror = Column(Text)
    compiler_errors = Column(Text)
    passed = Column(Boolean)

    iteration = relationship("Iteration", back_populates="test_cases")
