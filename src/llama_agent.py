import asyncio
import logging
from models import TestCase
from pipeline import CodeGenerationPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    pipeline = CodeGenerationPipeline(
        api_key="",
        base_url="https://api.sambanova.ai/v1",
        max_iterations=3
    )
    
    # Define test cases as a list of TestCase objects
    test_cases = [
        TestCase(input="2 3", expected_output="5"),
        TestCase(input="-1 1", expected_output="0")
    ]
    
    result = await pipeline.run_pipeline(
        language="py",
        question="Write a function that returns the sum of two numbers",
        test_cases=test_cases,
        explanation="Create a simple function that takes two numbers as input and returns their sum.",
        user_input="2 3"  # Example input for testing
    )
    
    # Display results
    print("=== Final Code ===")
    print(result.final_code)
    print("\n=== Execution Result ===")
    print(result.final_result.output)
    print("\n=== Test Case Results ===")
    for test_result in result.test_results:
        print(f"Input: {test_result['input']}")
        print(f"Expected Output: {test_result['expected_output']}")
        print(f"Actual Output: {test_result['actual_output']}")
        print(f"Passed: {test_result['passed']}")
        if test_result["error"]:
            print(f"Error: {test_result['error']}")
        print("-" * 40)
    print("\n=== Pipeline Metadata ===")
    print(f"Total Iterations: {result.iterations}")
    print(f"Success: {result.success}")

if __name__ == "__main__":
    asyncio.run(main())