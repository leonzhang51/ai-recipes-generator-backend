# AI Recipe & Shopping Engine - Backend Context

> **For Copilot:** This file provides context about the backend service. Read this to understand the architecture and implement features correctly.

## Project Overview

A FastAPI backend that generates structured recipes using local AI (LM Studio + PydanticAI).

| Attribute     | Value                                   |
| ------------- | --------------------------------------- |
| **Framework** | FastAPI + Python 3.12+                  |
| **AI**        | PydanticAI + LangGraph                  |
| **LLM**       | LM Studio at `http://localhost:1234/v1` |
| **Database**  | PostgreSQL 17 + pgvector                |
| **Frontend**  | Next.js 16.1.1 (separate repo)          |

---

## Current Implementation Status

### ✅ Completed

- `app/main.py` - FastAPI entry point with CORS
- `app/api/routes.py` - Basic router scaffold
- `app/core/config.py` - Basic config class
- `Dockerfile` - Container setup

### ❌ TODO (Priority Order)

1. **Models** (`app/models/`) - Pydantic schemas for Recipe, Ingredient, ShoppingList
2. **Settings** (`app/core/settings.py`) - LM Studio connection config
3. **Agents** (`app/agents/`) - PydanticAI recipe generator, LangGraph verification
4. **Recipe API** (`app/api/recipes.py`) - POST /api/recipes/generate endpoint
5. **Database** (`app/database/`) - PostgreSQL/pgvector integration

---

## Target Directory Structure

```
app/
├── main.py                 ✅ FastAPI entry point
├── api/
│   ├── routes.py           🔶 Basic routes
│   └── recipes.py          ❌ Recipe generation endpoint
├── core/
│   ├── config.py           🔶 Basic config
│   └── settings.py         ❌ Pydantic Settings (LM Studio URL, DB)
├── models/                  ❌ Create folder
│   ├── recipe.py           ❌ Recipe, Ingredient schemas
│   └── shopping_list.py    ❌ ShoppingList, ShoppingItem schemas
├── agents/                  ❌ Create folder
│   ├── recipe_agent.py     ❌ PydanticAI recipe generator
│   └── verification.py     ❌ LangGraph verification
└── database/                ❌ Create folder
    ├── connection.py       ❌ Async PostgreSQL
    └── repositories.py     ❌ Recipe CRUD
```

---

## API Contract

### POST /api/recipes/generate

**Request:**

```json
{
  "prompt": "healthy chicken dinner for 4",
  "dietary_preferences": ["gluten-free"],
  "cuisine_type": "mediterranean"
}
```

**Response:**

```json
{
  "id": "uuid",
  "title": "Mediterranean Grilled Chicken",
  "servings": 4,
  "prep_time_minutes": 15,
  "cook_time_minutes": 25,
  "ingredients": [
    {
      "name": "chicken breast",
      "amount": 4,
      "unit": "pieces",
      "aisle": "Meat & Poultry"
    }
  ],
  "instructions": [
    {
      "step": 1,
      "description": "Preheat grill to medium-high",
      "duration_minutes": 5
    }
  ],
  "shopping_list": {
    "Meat & Poultry": ["4 chicken breasts"],
    "Produce": ["2 lemons"]
  }
}
```

---

## Coding Standards

- **Validation:** Always use Pydantic v2 models for request/response
- **Naming:** PEP 8 (snake_case for functions/variables)
- **Async:** Use async/await for all I/O operations
- **Error Handling:** FastAPI exception handlers + middleware
- **AI Logic:** Use `pydantic-ai` for structured LLM outputs

---

## Dependencies Needed

```txt
# requirements.txt (update)
fastapi
uvicorn
pydantic>=2.0
pydantic-ai
langgraph
asyncpg
pgvector
python-dotenv
httpx
```

---

## Quick Start

```bash
# Activate environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --port 8000

# Start LM Studio on port 1234
```

---

## Cross-Repo Integration

The frontend (Next.js) calls this backend via Server Actions:

- **Endpoint:** `http://localhost:8000/api/recipes/generate`
- **CORS:** Already configured for `localhost:3000`

To work on full-stack features, attach the frontend repo's `CONTEXT.MD` to the chat.
