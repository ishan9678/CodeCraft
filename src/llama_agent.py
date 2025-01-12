import asyncio
import logging
from pipeline import CodeGenerationPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    pipeline = CodeGenerationPipeline(
        api_key="",
        base_url="https://api.sambanova.ai/v1",
        max_iterations=3
    )
    
    result = await pipeline.run_pipeline(
        language="py",
        question="Write a function that returns the sum of two numbers",
        test_cases="Test Case 1: Input: 2, 3 Output: 5\nTest Case 2: Input: -1, 1 Output: 0",
        explanation="Create a simple function that takes two numbers as input and returns their sum.",
        user_input="2 3"  # Example input for testing
    )
    
    # Display results
    print("=== Final Code ===")
    print(result.final_code)
    print("\n=== Execution Result ===")
    print(result.final_result.output)
    print("\n=== Pipeline Metadata ===")
    print(f"Total Iterations: {result.iterations}")
    print(f"Success: {result.success}")

if __name__ == "__main__":
    asyncio.run(main())