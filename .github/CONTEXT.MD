# AI Recipe & Shopping Engine - Backend Context

> **For Copilot:** This file provides context about the backend service. Read this to understand the architecture and implement features correctly.

## Project Overview

A FastAPI backend that generates structured recipes using local AI (LM Studio + PydanticAI).

| Attribute         | Value                                             |
| ----------------- | ------------------------------------------------- |
| **Framework**     | FastAPI + Python 3.13                             |
| **AI**            | PydanticAI 1.39.0 + LangGraph (planned)           |
| **Chat Model**    | qwen3-vl-4b-instruct-mlx via LM Studio            |
| **Embedding**     | text-embedding-embeddinggemma-300m-qat (768 dims) |
| **LM Studio URL** | `http://127.0.0.1:1234/v1`                        |
| **Database**      | PostgreSQL + pgvector (database: recipes)         |
| **Frontend**      | Next.js 16.1.1 (separate repo)                    |

---

## Current Implementation Status

### ✅ Completed (Phase 1 - Backend Core)

- `app/main.py` - FastAPI entry point with DB lifecycle management
- `app/api/routes.py` - Basic router
- `app/api/recipes.py` - Full CRUD + generate + similarity search
- `app/core/config.py` - Basic config class
- `app/core/settings.py` - Pydantic Settings with LM Studio + DB config
- `app/models/recipe.py` - Recipe, Ingredient, Instruction schemas
- `app/models/shopping_list.py` - ShoppingList, ShoppingItem schemas
- `app/agents/recipe_agent.py` - PydanticAI recipe generator
- `app/agents/embedding_agent.py` - Vector embedding generation
- `app/database/connection.py` - Async PostgreSQL + pgvector
- `app/database/models.py` - SQLAlchemy RecipeDB with Vector(768)
- `app/database/repositories.py` - Recipe CRUD + similarity operations
- `.env` - Environment configuration
- `Dockerfile` - Container setup

### ❌ TODO (Phase 2)

1. **LangGraph Verification** (`app/agents/verification.py`) - Ingredient-instruction consistency
2. **Frontend Integration** - Server Actions, types sync
3. **Recipe History** - User sessions, favorites
4. **Caching** - Redis for frequent queries

---

## Directory Structure

```
app/
├── main.py                 ✅ FastAPI entry point with DB lifecycle
├── api/
│   ├── routes.py           ✅ Basic routes
│   └── recipes.py          ✅ Full recipe CRUD + similarity search
├── core/
│   ├── config.py           ✅ Basic config
│   └── settings.py         ✅ Pydantic Settings (LM Studio, DB)
├── models/
│   ├── recipe.py           ✅ Recipe, Ingredient, Instruction schemas
│   └── shopping_list.py    ✅ ShoppingList, ShoppingItem schemas
├── agents/
│   ├── recipe_agent.py     ✅ PydanticAI recipe generator
│   ├── embedding_agent.py  ✅ Vector embedding for similarity
│   └── verification.py     ❌ LangGraph verification (Phase 2)
└── database/
    ├── connection.py       ✅ Async PostgreSQL + pgvector
    ├── models.py           ✅ SQLAlchemy RecipeDB model
    └── repositories.py     ✅ Recipe CRUD operations
```

---

## API Endpoints

### Health Check

```
GET /api/recipes/health
Response: {"status": "healthy", "service": "recipe-generator"}
```

### Generate Recipe

```
POST /api/recipes/generate
```

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
  "recipe": {
    "title": "Mediterranean Grilled Chicken",
    "description": "A flavorful grilled chicken dish...",
    "servings": 4,
    "prep_time_minutes": 15,
    "cook_time_minutes": 25,
    "ingredients": [
      {
        "name": "chicken breast",
        "amount": 4,
        "unit": "pieces",
        "aisle": "Meat & Poultry",
        "notes": null
      }
    ],
    "instructions": [
      {
        "step": 1,
        "description": "Preheat grill to medium-high",
        "duration_minutes": 5,
        "ingredients_used": ["chicken breast"]
      }
    ]
  },
  "shopping_list": {
    "Meat & Poultry": ["4 pieces chicken breast"],
    "Produce": ["1 lemon"]
  }
}
```

### Get Recipe by ID

```
GET /api/recipes/{id}
```

### Find Similar Recipes

```
GET /api/recipes/{id}/similar?limit=5
```

### List Recent Recipes

```
GET /api/recipes/?limit=20&search=chicken
```

### Delete Recipe

```
DELETE /api/recipes/{id}
```

---

## Coding Standards

- **Validation:** Always use Pydantic v2 models for request/response
- **Naming:** PEP 8 (snake_case for functions/variables)
- **Async:** Use async/await for all I/O operations
- **Error Handling:** FastAPI exception handlers + middleware
- **AI Logic:** Use `pydantic-ai` for structured LLM outputs

---

## Dependencies (requirements.txt)

```txt
fastapi>=0.127.0
uvicorn>=0.34.0
pydantic>=2.0
pydantic-ai>=1.39.0
pydantic-settings>=2.6.1
asyncpg>=0.30.0
pgvector>=0.4.2
sqlalchemy>=2.0.45
python-dotenv>=1.0.1
httpx>=0.28.1
```

---

## Quick Start

```bash
# Activate environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL & LM Studio first, then:
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test endpoints
curl http://localhost:8000/api/recipes/health
curl -X POST http://localhost:8000/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "healthy chicken dinner"}'
```

---

## Cross-Repo Integration

The frontend (Next.js) calls this backend via Server Actions:

- **Endpoint:** `http://localhost:8000/api/recipes/generate`
- **CORS:** Already configured for `localhost:3000`

To work on full-stack features, attach the frontend repo's `CONTEXT.MD` to the chat.
