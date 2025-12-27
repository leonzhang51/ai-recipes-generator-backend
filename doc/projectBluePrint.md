# AI Recipe & Shopping Engine (2025)

## 1. Project Overview

A dual-stack application that generates structured recipes and categorized shopping lists from natural language prompts.

| Attribute   | Value                                                                                                                |
| ----------- | -------------------------------------------------------------------------------------------------------------------- |
| **Goal**    | Transform ideas (e.g., "healthy chicken dinner") into validated step-by-step guides + aisle-organized shopping lists |
| **Date**    | December 2025                                                                                                        |
| **Privacy** | 100% Local AI inference via LM Studio                                                                                |

---

## 2. Tech Stack & Environment

### Frontend (Next.js 16.1.1)

- **Architecture:** App Router, Server Actions, React 19
- **UI Library:** shadcn/ui (Radix + Tailwind), Lucide-react icons
- **Key Features:** Partial Prerendering (PPR) for instant UI feedback
- **State:** Server-side for recipe data; Client-side for shopping list checkboxes

### Backend (Python 3.12+ / FastAPI)

- **AI Orchestration:** PydanticAI for structured output; LangGraph for multi-step verification
- **Local LLM:** LM Studio at `http://localhost:1234/v1` (OpenAI-compatible)
- **Database:** PostgreSQL 17 with pgvector for semantic recipe search

---

## 3. System Architecture & Workflow

```
┌─────────────────┐     Server Action     ┌─────────────────┐
│   Next.js 16    │ ──────────────────▶   │   FastAPI       │
│   (Frontend)    │                       │   (Backend)     │
└────────┬────────┘                       └────────┬────────┘
         │                                         │
         │                                         ▼
         │                                ┌─────────────────┐
         │                                │   LM Studio     │
         │                                │   (Local LLM)   │
         │                                └────────┬────────┘
         │                                         │
         │                                         ▼
         │                                ┌─────────────────┐
         │                                │   PydanticAI    │
         │                                │   (Structured)  │
         │                                └────────┬────────┘
         │                                         │
         │                                         ▼
         │                                ┌─────────────────┐
         │                                │   LangGraph     │
         │                                │   (Verification)│
         │                                └────────┬────────┘
         │                                         │
         │      JSON Recipe Response               │
         │ ◀───────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  UI Rendering   │
│  • How-To Cards │
│  • Shopping List│
└─────────────────┘
```

### Workflow Steps:

1. **User Input:** Next.js sends prompt to FastAPI via Server Action
2. **AI Processing:**
   - Step A: FastAPI calls LM Studio
   - Step B: PydanticAI forces typed JSON (Title, Ingredients, Instructions)
   - Step C: LangGraph verifies ingredient-instruction consistency
3. **Data Storage:** Recipe embedding stored in pgvector for similarity search
4. **Delivery:** Next.js renders structured JSON into How-To Guide + Shopping List

---

## 4. Implementation Progress Tracker

### Backend Status

| Component           | File                            | Status  | Description                                  |
| ------------------- | ------------------------------- | ------- | -------------------------------------------- |
| FastAPI Entry       | `app/main.py`                   | ✅ Done | CORS, router, DB lifecycle                   |
| API Routes          | `app/api/routes.py`             | ✅ Done | Basic endpoints                              |
| Recipe API          | `app/api/recipes.py`            | ✅ Done | Full CRUD + generate + similarity search     |
| Config              | `app/core/config.py`            | ✅ Done | Basic config class                           |
| Settings            | `app/core/settings.py`          | ✅ Done | Pydantic Settings with LM Studio + DB config |
| **Pydantic Models** | `app/models/recipe.py`          | ✅ Done | Recipe, Ingredient, Instruction schemas      |
| **Shopping List**   | `app/models/shopping_list.py`   | ✅ Done | ShoppingList, ShoppingItem schemas           |
| **Recipe Agent**    | `app/agents/recipe_agent.py`    | ✅ Done | PydanticAI + OpenAIChatModel for LM Studio   |
| **Embedding Agent** | `app/agents/embedding_agent.py` | ✅ Done | Vector embeddings for similarity search      |
| **DB Connection**   | `app/database/connection.py`    | ✅ Done | Async PostgreSQL + pgvector                  |
| **DB Models**       | `app/database/models.py`        | ✅ Done | SQLAlchemy RecipeDB with Vector(768)         |
| **Repository**      | `app/database/repositories.py`  | ✅ Done | Recipe CRUD + similarity search operations   |
| **Verification**    | `app/agents/verification.py`    | ❌ TODO | LangGraph verification graph (Phase 2)       |

### Frontend Status

| Component             | File                                  | Status  | Description                                       |
| --------------------- | ------------------------------------- | ------- | ------------------------------------------------- |
| Home Page             | `app/page.tsx`                        | ✅ Done | Hero, CTA sections                                |
| Recipe Generator Form | `components/home/RecipeGenerator.tsx` | ✅ Done | Input form (simulated API)                        |
| UI Components         | `components/ui/`                      | ✅ Done | button, card, checkbox, input, label, scroll-area |
| Layout                | `components/layout/`                  | ✅ Done | Header, Footer                                    |
| **Server Actions**    | `app/actions/`                        | ❌ TODO | Backend API calls                                 |
| **Recipe Page**       | `app/recipe/[id]/`                    | ❌ TODO | Dynamic recipe view                               |
| **Generate Page**     | `app/generate/`                       | ❌ TODO | Full generation flow                              |
| **Recipe Types**      | `types/recipe.ts`                     | ❌ TODO | Recipe, Ingredient interfaces                     |
| **Shopping List**     | `components/recipe/ShoppingList.tsx`  | ❌ TODO | Aisle-grouped checklist                           |
| **How-To Guide**      | `components/recipe/HowToGuide.tsx`    | ❌ TODO | Step-by-step cards                                |

### Infrastructure Status

| Component             | Status  | Notes                                                   |
| --------------------- | ------- | ------------------------------------------------------- |
| Docker                | ✅ Done | Dockerfile exists                                       |
| PostgreSQL + pgvector | ✅ Done | Running locally, database "recipes" created             |
| LM Studio             | ✅ Done | Running at http://127.0.0.1:1234                        |
| Chat Model            | ✅ Done | qwen3-vl-4b-instruct-mlx loaded                         |
| Embedding Model       | ✅ Done | text-embedding-embeddinggemma-300m-qat (768 dimensions) |
| Environment Config    | ✅ Done | .env file with all settings                             |

---

## 5. Directory Structure (Current vs Target)

### Backend (ai-recipes-generator-backend)

```
app/
├── __init__.py
├── main.py                 ✅ FastAPI entry point with DB lifecycle
├── api/
│   ├── __init__.py
│   ├── routes.py           ✅ Basic routes
│   └── recipes.py          ✅ Full recipe CRUD + generate + similarity
├── core/
│   ├── config.py           ✅ Basic config
│   └── settings.py         ✅ Pydantic Settings with all config
├── models/
│   ├── __init__.py         ✅ Package init
│   ├── recipe.py           ✅ Recipe, Ingredient, Instruction schemas
│   └── shopping_list.py    ✅ ShoppingList, ShoppingItem schemas
├── agents/
│   ├── __init__.py         ✅ Package init
│   ├── recipe_agent.py     ✅ PydanticAI recipe generator
│   ├── embedding_agent.py  ✅ Vector embedding generation
│   └── verification.py     ❌ TODO: LangGraph verification (Phase 2)
└── database/
    ├── __init__.py         ✅ Package init
    ├── connection.py       ✅ Async PostgreSQL + pgvector
    ├── models.py           ✅ SQLAlchemy RecipeDB model
    └── repositories.py     ✅ Recipe CRUD + similarity operations
```

### Frontend (AI-recipes-generator)

```
app/
├── page.tsx                ✅ Home page
├── layout.tsx              ✅ Root layout
├── globals.css             ✅ Tailwind styles
├── actions/                 ❌ TODO: Create folder
│   └── recipe.ts           ❌ Server actions for API
├── generate/                ❌ TODO: Create folder
│   └── page.tsx            ❌ Generation flow page
└── recipe/                  ❌ TODO: Create folder
    └── [id]/
        └── page.tsx        ❌ Dynamic recipe view

components/
├── home/
│   ├── RecipeGenerator.tsx ✅ Input form
│   ├── FeatureShowcase.tsx ✅ Features section
│   └── Testimonials.tsx    ✅ Social proof
├── layout/
│   ├── Header.tsx          ✅ Navigation
│   └── Footer.tsx          ✅ Footer
├── recipe/                  ❌ TODO: Create folder
│   ├── HowToGuide.tsx      ❌ Step-by-step cards
│   ├── ShoppingList.tsx    ❌ Aisle-grouped checklist
│   └── RecipeCard.tsx      ❌ Recipe preview card
└── ui/                      ✅ shadcn/ui components

types/
├── products.ts             ✅ Product interfaces (legacy?)
├── css.d.ts                ✅ CSS module types
└── recipe.ts                ❌ TODO: Recipe interfaces
```

---

## 6. Coding Standards

### Python (Backend)

- **Typing:** Always use Pydantic v2 models for request/response
- **Naming:** PEP 8 (snake_case for functions/variables)
- **Error Handling:** FastAPI exception handlers + middleware
- **Async:** Use async/await for all I/O operations

### TypeScript (Frontend)

- **Typing:** Strict TypeScript interfaces in `types/`
- **Components:** MVP pattern (Model-View-Presenter)
- **UI Library:** shadcn/ui components first
- **Forms:** react-hook-form + zod validation
- **Security:** Avoid old-pattern middleware (CVE-2025-55184)

---

## 7. Implementation Roadmap

### Phase 1: Backend Core (Priority: HIGH)

1. [ ] Create Pydantic models (`models/recipe.py`, `models/shopping_list.py`)
2. [ ] Set up LM Studio connection (`core/settings.py`)
3. [ ] Implement PydanticAI recipe agent (`agents/recipe_agent.py`)
4. [ ] Create recipe generation endpoint (`api/recipes.py`)

### Phase 2: Frontend Integration (Priority: HIGH)

1. [ ] Create TypeScript interfaces (`types/recipe.ts`)
2. [ ] Implement Server Actions (`app/actions/recipe.ts`)
3. [ ] Build generate page (`app/generate/page.tsx`)
4. [ ] Connect RecipeGenerator to real API

### Phase 3: Recipe Display (Priority: MEDIUM)

1. [ ] Build HowToGuide component (`components/recipe/HowToGuide.tsx`)
2. [ ] Build ShoppingList component (`components/recipe/ShoppingList.tsx`)
3. [ ] Create dynamic recipe page (`app/recipe/[id]/page.tsx`)

### Phase 4: Database & Verification (Priority: MEDIUM)

1. [ ] Set up PostgreSQL + pgvector (docker-compose)
2. [ ] Implement database layer (`database/`)
3. [ ] Add LangGraph verification (`agents/verification.py`)
4. [ ] Implement similarity search

### Phase 5: Polish (Priority: LOW)

1. [ ] Add loading states and error handling
2. [ ] Implement recipe history/favorites
3. [ ] Add unit tests
4. [ ] Production deployment config

---

## 8. API Contract (Target)

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
  "description": "A healthy, flavorful dish...",
  "servings": 4,
  "prep_time_minutes": 15,
  "cook_time_minutes": 25,
  "ingredients": [
    {
      "name": "chicken breast",
      "amount": 4,
      "unit": "pieces",
      "aisle": "Meat & Poultry",
      "notes": "boneless, skinless"
    }
  ],
  "instructions": [
    {
      "step": 1,
      "description": "Preheat grill to medium-high heat",
      "duration_minutes": 5,
      "ingredients_used": []
    }
  ],
  "shopping_list": {
    "Meat & Poultry": ["4 chicken breasts"],
    "Produce": ["2 lemons", "fresh oregano"],
    "Pantry": ["olive oil", "garlic"]
  }
}
```

---

## 9. Quick Start

### Backend

```bash
cd ai-recipes-generator-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd AI-recipes-generator
npm install
npm run dev
```

### LM Studio

1. Download and install LM Studio
2. Load a compatible model (e.g., Mistral, Llama)
3. Start the local server on port 1234
