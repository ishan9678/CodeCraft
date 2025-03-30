# CodeCraft

CodeCraft is an AI-powered iterative code refinement tool that utilizes Large Language Models (LLMs) to generate, test, and refine code until it meets the expected output. It follows a structured feedback loop incorporating Chain of Thought prompting techniques for enhanced reasoning and explainability.

## Features
- **Automated Code Generation**: Generates code based on a given programming question, example input, and language.
- **Iterative Refinement**: Uses test cases and feedback loops to debug and enhance code quality.
- **Edge Case Handling**: Automatically generates five test cases, including edge cases.
- **Compiler Execution**: Runs the generated code and verifies outputs against expected results.
- **LLM Debugging Assistance**: If the output doesn't match expectations, the model iteratively refines the code.
- **Supports Multiple Programming Languages**: Users can specify their preferred language for code generation.
- **Groq API Integration**: Users can input their Groq API key to interact with the application.

## Deployment
Deployed URL: [http://139.59.68.177:3000/](http://139.59.68.177:3000/)

## Backend
The backend is built using **FastAPI** and utilizes **PostgreSQL** as its database.

### Setup Instructions
1. **Set up environment variables:**
   Create a `.env` file in the root directory with the following variables:
   ```ini
   COMPILER_API_ENDPOINT=
   DATABASE_URL=
   CORS_ORIGINS=
   ```
   - `COMPILER_API_ENDPOINT`: URL of Judge0 API (either self-hosted or from [RapidAPI](https://rapidapi.com/judge0-official/api/judge0-ce)).
   - `DATABASE_URL`: PostgreSQL database connection string.
   - `CORS_ORIGINS`: Allowed origins for CORS ie http://localhost:3000 for frontend

2. **Set up a Python virtual environment:**
   ```sh
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Run database migrations:**
   ```sh
   cd backend/src
   alembic upgrade head
   ```

4. **Start the server:**
   ```sh
   cd backend/src
   uvicorn llama_agent:app --reload
   ```

## Frontend
The frontend is built using **Next.js**.

### Setup Instructions
1. **Navigate to the frontend directory:**
   ```sh
   cd frontend
   ```
2. **Create an `.env` file:** Copy `.env.example` and fill in the necessary values:
   ```ini
   NEXT_PUBLIC_API_URL=
   ```
3. **Install dependencies and start the frontend:**
   ```sh
   yarn install
   yarn dev
   ```

## Workflow Overview
1. **User Input:**
   - Model selection
   - Programming question
   - Language
   - Example input
   - Number of iterations
2. **Test Case Generation:**
   - The model generates five test cases, including edge cases.
3. **Code Generation:**
   - Code is generated based on the input parameters.
4. **Compilation and Execution:**
   - The code is compiled and executed using the Judge0 API.
5. **Verification:**
   - The output is compared with expected results.
6. **Feedback Loop:**
   - If errors occur or outputs do not match, additional debugging information is fed back to the model for refinement.
7. **Final Output:**
   - Once the expected output is achieved, the final refined code is presented to the user.

## Contributing
Contributions are welcome! Feel free to fork this repo and submit pull requests.

## License
This project is licensed under the MIT License.

