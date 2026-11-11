# LangGraph Quiz Generator

An AI-powered quiz generation and evaluation application built using **LangGraph, LangChain, Amazon Bedrock, FastAPI, and PostgreSQL**. The application uses multiple AI agents to generate quiz questions, collect user answers, evaluate responses, and provide scores with explanations and feedback.

## Features

- **AI-powered quiz generation:** Generates quiz questions based on the user's topic or query.
- **Multi-agent workflow:** Uses LangGraph to coordinate quiz generation and answer evaluation agents.
- **Answer evaluation:** Evaluates submitted answers and calculates correct and incorrect counts.
- **Personalized feedback:** Provides explanations for incorrect answers and overall performance feedback.
- **Conversation persistence:** Uses PostgreSQL checkpointing to maintain workflow state.
- **Guardrails:** Applies an LLM-based guardrail before processing user queries.
- **REST API:** Exposes the quiz workflow through a FastAPI endpoint.
- **Structured responses:** Uses Pydantic models to structure quiz and review outputs.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| API Framework | FastAPI |
| Agent Orchestration | LangGraph |
| LLM Framework | LangChain |
| LLM Provider | Amazon Bedrock |
| Database | PostgreSQL |
| Database Checkpointing | LangGraph PostgreSQL Checkpointer |
| Data Validation | Pydantic |
| Server | Uvicorn |

## Architecture

The application follows a multi-agent architecture:

1. **API Layer:** Receives user requests through the FastAPI endpoint.
2. **Guardrail Layer:** Checks whether the user's query can proceed.
3. **Main Agent:** Orchestrates the quiz generation and review workflow.
4. **Quiz Agent:** Generates quiz questions using the configured LLM.
5. **Review Agent:** Evaluates user answers and generates scores, explanations, and feedback.
6. **State Management:** Uses LangGraph state and PostgreSQL checkpointing to preserve workflow information.

## Project Structure

```text
task_11_final/
│
├── .env.example
├── .gitignore
├── README.md
│
├── design/
│   ├── agent_client_sequence.wsd
│   ├── agen_client_class.puml
│   └── api.yaml
│
└── dev/
    └── mcp client/
        ├── pyproject.toml
        ├── uv.lock
        │
        └── src/
            ├── app.py
            ├── setting.py
            │
            ├── agents/
            │   ├── main_agent.py
            │   ├── main_prompt.py
            │   ├── middleware.py
            │   └── state.py
            │
            ├── tools/
            │   ├── quiz_agent.py
            │   ├── review_agent.py
            │   ├── quiz_prompt.py
            │   └── review_prompt.py
            │
            ├── routes/
            │   └── agent_router.py
            │
            ├── services/
            │   └── agent_service.py
            │
            ├── dependency/
            │   └── dependency.py
            │
            ├── models/
            │   └── request_dto.py
            │
            └── utils/
                ├── bedrock_client.py
                ├── llm_client.py
                └── ...
```

## Prerequisites

Before running the application, ensure you have:

- Python 3.14 or later.
- [uv](https://docs.astral.sh/uv/) package manager.
- PostgreSQL installed and running.
- An AWS account with access to Amazon Bedrock.
- Access to a compatible Bedrock foundation model.

## Configuration

1. Create a `.env` file in the project root (`task_11_final`).
2. Copy the contents of `.env.example` into `.env`.
3. Update the values with your local database and AWS configuration.

Required environment variables:

```env
# PostgreSQL Configuration
DB_PORT=5432
DB_HOST=localhost
DB_NAME=agent_as_tool_db
DB_USERNAME=postgres
DB_PASSWORD=your_database_password

# Application Configuration
PORT=8080
HOST=0.0.0.0
LOG_LEVEL=INFO

# Amazon Bedrock Configuration
REGION=your_aws_region
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
MODEL_ID=your_bedrock_model_id
```

**Important:** Never commit your `.env` file or expose AWS credentials and database passwords in the repository.

Create the PostgreSQL database specified by `DB_NAME` before starting the application.

## Installation

Open a terminal and navigate to the application directory:

```bash
cd "dev/mcp client"
```

Install the project dependencies:

```bash
uv sync
```

## Running the Application

From the `dev/mcp client` directory, run:

```bash
uv run uvicorn app:app --app-dir src --reload --host 0.0.0.0 --port 8080
```

The application will be available at:

```text
http://localhost:8080
```

## API Documentation

FastAPI provides interactive API documentation.

- **Swagger UI:** http://localhost:8080/docs
- **ReDoc:** http://localhost:8080/redoc

### Generate and Review Quiz

**Endpoint:**

```http
POST /api/v1/quiz-agent
```

**Request Body:**

```json
{
  "user_id": "user123",
  "user_query": "Generate a quiz about Python programming"
}
```

**Response fields:**

| Field | Description |
|---|---|
| correct_count | Number of correct answers |
| wrong_count | Number of incorrect answers |
| grade | Overall quiz grade |
| wrong_explanations | Explanations for incorrect answers |
| feedback | Overall performance feedback |
| thread_id | Workflow conversation identifier |

## Workflow

```text
User Query
    |
    v
FastAPI Endpoint
    |
    v
LLM Guardrail
    |
    v
Main LangGraph Agent
    |
    v
Quiz Generation Agent
    |
    v
Answer Collection
    |
    v
Review Agent
    |
    v
Score + Explanations + Feedback
    |
    v
API Response
```

## Future Enhancements

- Move answer collection from terminal input to dedicated API endpoints.
- Add a web-based quiz interface.
- Support configurable question counts and difficulty levels.
- Add user authentication and quiz history.
- Improve automated testing and evaluation.