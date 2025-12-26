# Backend Coding Instructions

- **Framework:** FastAPI with Python 3.12+.
- **Validation:** Always use Pydantic v2 models for request/response bodies.
- **AI Logic:** Use `pydantic-ai` for structured LLM outputs.
- **Database:** Use SQLAlchemy with async drivers; all vector operations must use `pgvector`.
- **Naming:** Follow PEP 8 (snake_case for functions/variables).
