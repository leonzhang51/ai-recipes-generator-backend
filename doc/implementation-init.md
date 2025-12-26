Backend Codebase (Python/FastAPI)
The backend acts as the "Brain," managing the LLM through LM Studio and data in PostgreSQL.
Setup Data Contracts: Define strict Pydantic models for the recipe and shopping list to ensure 100% valid JSON responses.
LLM Integration (PydanticAI + LM Studio): Configure a PydanticAI agent to use the OpenAI-compatible endpoint provided by LM Studio (default: http://localhost:1234/v1).
Database Management: Use SQLAlchemy or SQLModel with the pgvector extension to store recipes and their semantic embeddings for future "similar recipe" searches.
Workflow Logic:
Generate Node: Prompts the local LLM to create the recipe and list.
Verify Node: Checks the output for specific dietary constraints or instruction clarity.
API Endpoint: Expose a POST /api/recipes/generate endpoint for the frontend.
GitHub Copilot Prompt for Backend:
"Create a FastAPI application using PydanticAI and SQLAlchemy. Set up a Pydantic model for a Recipe with ingredients (list) and steps (list). Configure a PydanticAI agent to use a local LLM at http://localhost:1234/v1 and write a POST endpoint that takes a user idea and returns the validated Recipe object."
