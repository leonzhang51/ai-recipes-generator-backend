# AI Recipe Generator - Technical Walkthrough

> **For New Developers** - Complete guide to understanding and working with the AI Recipe Generator system.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Backend Deep Dive](#backend-deep-dive)
4. [Frontend Deep Dive](#frontend-deep-dive)
5. [Data Flow](#data-flow)
6. [AI System](#ai-system)
7. [Database](#database)
8. [API Reference](#api-reference)
9. [Development Setup](#development-setup)
10. [Common Tasks](#common-tasks)

---

## System Overview

The AI Recipe Generator is a full-stack application that uses local LLMs (via LM Studio) to generate recipes from natural language prompts. The system consists of:

| Component      | Technology            | Port | Purpose                        |
| -------------- | --------------------- | ---- | ------------------------------ |
| **Frontend**   | Next.js 16 + React 19 | 3000 | User interface                 |
| **Backend**    | FastAPI + Python 3.13 | 8000 | API & AI orchestration         |
| **Database**   | PostgreSQL + pgvector | 5432 | Recipe storage & vector search |
| **LLM Server** | LM Studio             | 1234 | Local AI inference             |

### Key Features

- 🤖 AI-powered recipe generation from natural language
- 🛒 Automatic shopping list organization by grocery aisle
- 🔍 Similar recipe recommendations using vector embeddings
- ⚡ Async/await throughout for optimal performance

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                    │
│                        (Next.js 16 / React 19)                          │
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │  /generate   │    │ /recipe/[id] │    │    Components            │  │
│  │    page      │    │    page      │    │  ┌────────────────────┐  │  │
│  └──────┬───────┘    └──────┬───────┘    │  │ RecipeHeader       │  │  │
│         │                   │            │  │ IngredientsList    │  │  │
│         ▼                   ▼            │  │ HowToGuide         │  │  │
│  ┌──────────────────────────────────┐    │  │ ShoppingList       │  │  │
│  │      Server Actions              │    │  │ RecipeCard         │  │  │
│  │   (app/actions/recipe.ts)        │    │  └────────────────────┘  │  │
│  └──────────────┬───────────────────┘    └──────────────────────────┘  │
└─────────────────┼───────────────────────────────────────────────────────┘
                  │ HTTP (fetch)
                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              BACKEND                                     │
│                      (FastAPI / Python 3.13)                            │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    API Layer (app/api/)                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │   │
│  │  │   /health   │  │  /generate  │  │  /{id}  /{id}/similar   │  │   │
│  │  └─────────────┘  └──────┬──────┘  └────────────┬────────────┘  │   │
│  └──────────────────────────┼──────────────────────┼────────────────┘   │
│                             │                      │                     │
│                             ▼                      ▼                     │
│  ┌────────────────────────────────┐    ┌────────────────────────────┐   │
│  │      AI Agents Layer           │    │    Repository Layer        │   │
│  │  ┌──────────────────────────┐  │    │  ┌──────────────────────┐  │   │
│  │  │  recipe_agent.py         │  │    │  │  repositories.py     │  │   │
│  │  │  (PydanticAI + LM Studio)│  │    │  │  (SQLAlchemy async)  │  │   │
│  │  ├──────────────────────────┤  │    │  └──────────┬───────────┘  │   │
│  │  │  embedding_agent.py      │  │    └─────────────┼──────────────┘   │
│  │  │  (Vector embeddings)     │  │                  │                   │
│  │  └──────────────────────────┘  │                  ▼                   │
│  └────────────────┬───────────────┘    ┌────────────────────────────┐   │
│                   │                    │    Database Layer          │   │
│                   │                    │  ┌──────────────────────┐  │   │
│                   │                    │  │  models.py (RecipeDB)│  │   │
│                   │                    │  │  + pgvector extension│  │   │
│                   │                    │  └──────────────────────┘  │   │
│                   │                    └─────────────┬──────────────┘   │
└───────────────────┼──────────────────────────────────┼──────────────────┘
                    │                                  │
                    ▼                                  ▼
┌───────────────────────────────┐    ┌───────────────────────────────────┐
│         LM Studio             │    │           PostgreSQL              │
│   (Local LLM Inference)       │    │     (with pgvector extension)     │
│                               │    │                                   │
│  Models:                      │    │  Tables:                          │
│  • qwen3-vl-4b-instruct-mlx   │    │  • recipes (with 768-dim vectors) │
│    (Chat/Instruct)            │    │                                   │
│  • embeddinggemma-300m-qat    │    │  Features:                        │
│    (Embeddings - 768 dims)    │    │  • JSONB for ingredients/steps    │
│                               │    │  • Vector similarity search       │
└───────────────────────────────┘    └───────────────────────────────────┘
```

---

## Backend Deep Dive

### Directory Structure

```
ai-recipes-generator-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point, lifespan events
│   ├── api/
│   │   ├── routes.py        # Legacy routes (can be removed)
│   │   └── recipes.py       # Recipe API endpoints ⭐
│   ├── agents/
│   │   ├── __init__.py      # Public exports
│   │   ├── recipe_agent.py  # PydanticAI recipe generation ⭐
│   │   └── embedding_agent.py # Vector embeddings ⭐
│   ├── core/
│   │   └── settings.py      # Pydantic Settings configuration
│   ├── database/
│   │   ├── connection.py    # Async SQLAlchemy engine & sessions
│   │   ├── models.py        # SQLAlchemy ORM models ⭐
│   │   └── repositories.py  # Repository pattern for DB ops ⭐
│   └── models/
│       └── recipe.py        # Pydantic models (API schemas)
├── tests/
├── doc/
├── pyproject.toml           # Python dependencies
└── requirements.txt
```

### Key Components

#### 1. **FastAPI Application** (`app/main.py`)

```python
# Lifespan manages startup/shutdown
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup: Initialize database connection pool
    await init_db()
    yield
    # Shutdown: Close connections
    await close_db()

# CORS configured for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js
    ...
)
```

#### 2. **Recipe Agent** (`app/agents/recipe_agent.py`)

Uses **PydanticAI** to enforce structured output from the LLM:

```python
# Define the exact output schema
class GeneratedRecipe(BaseModel):
    title: str
    description: str
    servings: int = Field(..., ge=1, le=20)
    prep_time_minutes: int
    cook_time_minutes: int
    ingredients: list[Ingredient]
    instructions: list[Instruction]

# Create the agent with LM Studio
agent = Agent(
    model=OpenAIChatModel("qwen3-vl-4b-instruct-mlx", provider=provider),
    output_type=GeneratedRecipe,  # Forces structured JSON output
    system_prompt=RECIPE_SYSTEM_PROMPT,
    retries=2,
)
```

**How it works:**

1. User prompt → Full prompt with dietary/cuisine context
2. Agent sends to LM Studio with JSON schema
3. LLM generates structured JSON response
4. PydanticAI validates and returns `GeneratedRecipe`

#### 3. **Embedding Agent** (`app/agents/embedding_agent.py`)

Generates vector embeddings for similarity search:

```python
async def generate_recipe_embedding(
    title: str,
    description: str,
    ingredients: list[str],
    cuisine_type: Optional[str] = None,
) -> Optional[list[float]]:
    # Combine recipe info into searchable text
    text = f"Recipe: {title}\nDescription: {description}\nIngredients: {', '.join(ingredients)}"

    # Call LM Studio embedding endpoint
    response = await client.post(
        "http://127.0.0.1:1234/v1/embeddings",
        json={"model": "text-embedding-embeddinggemma-300m-qat", "input": text}
    )
    return response["data"][0]["embedding"]  # 768-dimensional vector
```

#### 4. **Repository Pattern** (`app/database/repositories.py`)

Clean separation of database operations:

```python
class RecipeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, recipe_response, embedding, ...) -> RecipeDB:
        """Create new recipe with embedding"""

    async def get_by_id(self, recipe_id: UUID) -> Optional[RecipeDB]:
        """Fetch single recipe"""

    async def find_similar(self, embedding: list[float], limit: int = 5):
        """Vector similarity search using pgvector"""
        query = (
            select(RecipeDB)
            .order_by(RecipeDB.embedding.cosine_distance(embedding))
            .limit(limit)
        )
```

---

## Frontend Deep Dive

### Directory Structure

```
AI-recipes-generator/
├── app/
│   ├── layout.tsx           # Root layout with header/footer
│   ├── page.tsx             # Home page
│   ├── globals.css          # Tailwind CSS
│   ├── actions/
│   │   └── recipe.ts        # Server Actions (API calls) ⭐
│   ├── generate/
│   │   ├── page.tsx         # Generation page (Server Component)
│   │   └── RecipeGeneratorForm.tsx  # Form (Client Component) ⭐
│   └── recipe/
│       └── [id]/
│           ├── page.tsx     # Recipe detail (Server Component)
│           └── not-found.tsx
├── components/
│   ├── home/
│   │   └── RecipeGenerator.tsx  # Home page CTA
│   ├── layout/
│   │   ├── Header.tsx
│   │   └── Footer.tsx
│   ├── recipe/              # Recipe display components ⭐
│   │   ├── index.ts         # Barrel export
│   │   ├── RecipeHeader.tsx
│   │   ├── IngredientsList.tsx
│   │   ├── HowToGuide.tsx
│   │   ├── ShoppingList.tsx
│   │   └── RecipeCard.tsx
│   └── ui/                  # shadcn/ui primitives
│       ├── button.tsx
│       ├── card.tsx
│       ├── checkbox.tsx
│       └── ...
├── types/
│   └── recipe.ts            # TypeScript interfaces ⭐
└── lib/
    └── utils.ts             # cn() helper for Tailwind
```

### MVP Pattern

The frontend follows **Model-View-Presenter** architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                         MODEL                               │
│  types/recipe.ts - TypeScript interfaces                    │
│  (Ingredient, Instruction, Recipe, ShoppingList, etc.)      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       PRESENTER                             │
│  RecipeGeneratorForm.tsx - Handles state & API calls        │
│  • useState for form inputs                                 │
│  • useTransition for loading states                         │
│  • Calls Server Actions (generateRecipe)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                          VIEW                               │
│  Pure presentational components:                            │
│  • RecipeHeader - Title, description, time badges           │
│  • IngredientsList - Ingredients grouped by aisle           │
│  • HowToGuide - Step-by-step instructions                   │
│  • ShoppingList - Checkable shopping list                   │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. **Server Actions** (`app/actions/recipe.ts`)

```typescript
"use server";

export async function generateRecipe(
  request: GenerateRecipeRequest,
): Promise<ActionResult<GenerateRecipeResponse>> {
  const response = await fetch(`${API_BASE_URL}/api/recipes/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    cache: "no-store",
  });

  if (!response.ok) {
    return { success: false, error: errorData.detail };
  }

  return { success: true, data: await response.json() };
}
```

**Why Server Actions?**

- Runs on server, not exposed to client
- Type-safe with TypeScript
- Automatic error handling
- Works with React's `useTransition`

#### 2. **Recipe Generator Form** (`app/generate/RecipeGeneratorForm.tsx`)

```tsx
"use client";

export function RecipeGeneratorForm() {
  const [isPending, startTransition] = useTransition();
  const [result, setResult] = useState<GenerateRecipeResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    startTransition(async () => {
      const response = await generateRecipe({
        prompt: prompt.trim(),
        dietary_preferences: selectedDietary,
        cuisine_type: selectedCuisine,
      });

      if (response.success) {
        setResult(response.data);
      }
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form inputs */}
      {isPending && <LoadingSpinner />}
      {result && (
        <>
          <RecipeHeader recipe={result.recipe} />
          <IngredientsList ingredients={result.recipe.ingredients} />
          <HowToGuide instructions={result.recipe.instructions} />
          <ShoppingList shoppingList={result.shopping_list} />
        </>
      )}
    </form>
  );
}
```

#### 3. **Shopping List Component** (`components/recipe/ShoppingList.tsx`)

```tsx
"use client";

export function ShoppingList({ shoppingList }: ShoppingListProps) {
  const [checkedItems, setCheckedItems] = useState<CheckedState>({});

  // Group by aisle with icons
  const AISLE_ICONS = {
    Produce: "🥬",
    "Meat & Poultry": "🍗",
    // ...
  };

  return (
    <Card>
      {Object.entries(shoppingList).map(([aisle, items]) => (
        <div key={aisle}>
          <h3>
            {AISLE_ICONS[aisle]} {aisle}
          </h3>
          {items.map((item, index) => (
            <Checkbox
              checked={checkedItems[aisle]?.[index]}
              onCheckedChange={() => handleToggle(aisle, index)}
            />
          ))}
        </div>
      ))}
    </Card>
  );
}
```

---

## Data Flow

### Recipe Generation Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 1. USER INPUT                                                            │
│    User types: "healthy chicken dinner for 4"                            │
│    Selects: Gluten-Free, Italian cuisine                                 │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ 2. FRONTEND (RecipeGeneratorForm)                                        │
│    • useTransition starts pending state                                  │
│    • Calls Server Action: generateRecipe()                               │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │ HTTP POST
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ 3. BACKEND API (/api/recipes/generate)                                   │
│    Request body:                                                         │
│    {                                                                     │
│      "prompt": "healthy chicken dinner for 4",                           │
│      "dietary_preferences": ["Gluten-Free"],                             │
│      "cuisine_type": "Italian"                                           │
│    }                                                                     │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ 4. RECIPE AGENT (PydanticAI)                                             │
│    • Builds full prompt with system context                              │
│    • Sends to LM Studio with JSON schema                                 │
│    • Receives structured GeneratedRecipe                                 │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ 5. POST-PROCESSING                                                       │
│    • build_shopping_list() groups ingredients by aisle                   │
│    • generate_recipe_embedding() creates 768-dim vector                  │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ 6. DATABASE (PostgreSQL + pgvector)                                      │
│    • RecipeRepository.create() saves:                                    │
│      - Recipe metadata (title, description, times)                       │
│      - Ingredients as JSONB array                                        │
│      - Instructions as JSONB array                                       │
│      - Shopping list as JSONB dict                                       │
│      - Embedding as Vector(768)                                          │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ 7. RESPONSE                                                              │
│    {                                                                     │
│      "id": "uuid-here",                                                  │
│      "recipe": { title, description, ingredients, instructions, ... },   │
│      "shopping_list": { "Produce": [...], "Meat & Poultry": [...] }     │
│    }                                                                     │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ 8. FRONTEND RENDER                                                       │
│    • RecipeHeader displays title, time badges                            │
│    • IngredientsList shows ingredients by aisle                          │
│    • HowToGuide renders step-by-step instructions                        │
│    • ShoppingList provides checkable grocery list                        │
└──────────────────────────────────────────────────────────────────────────┘
```

### Similar Recipes Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ GET /recipes/   │     │ RecipeRepository│     │    pgvector     │
│   {id}/similar  │────▶│ .find_similar() │────▶│ cosine_distance │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │ Top 5 most      │
                                               │ similar recipes │
                                               └─────────────────┘
```

---

## AI System

### Models Used

| Model                      | Purpose           | Dimensions | Provider  |
| -------------------------- | ----------------- | ---------- | --------- |
| `qwen3-vl-4b-instruct-mlx` | Recipe generation | N/A        | LM Studio |
| `embeddinggemma-300m-qat`  | Vector embeddings | 768        | LM Studio |

### System Prompt

The recipe agent uses a carefully crafted system prompt:

```
You are an expert chef and recipe developer. Your task is to create detailed,
accurate, and delicious recipes based on user requests.

When generating recipes:
1. Create realistic, tested-quality recipes with accurate measurements
2. Assign each ingredient to an appropriate grocery aisle category:
   - Produce (fruits, vegetables, herbs)
   - Meat & Poultry
   - Seafood
   - Dairy & Eggs
   - Bakery
   - Frozen Foods
   - Pantry (oils, spices, canned goods, pasta, rice)
   - Beverages
   - Condiments & Sauces
3. Ensure every ingredient listed is used in at least one instruction step
4. Include the ingredient names used in each instruction's ingredients_used field
5. Provide realistic prep and cook times
6. Write clear, detailed instructions that a home cook can follow
```

### Structured Output

PydanticAI forces the LLM to output valid JSON matching our schema:

```python
class Ingredient(BaseModel):
    name: str
    amount: float
    unit: str
    aisle: str  # Must be valid aisle category
    notes: Optional[str]

class Instruction(BaseModel):
    step: int
    description: str
    duration_minutes: Optional[int]
    ingredients_used: list[str]  # References ingredient names
```

---

## Database

### Schema

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE recipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Recipe metadata
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    servings INTEGER NOT NULL,
    prep_time_minutes INTEGER NOT NULL,
    cook_time_minutes INTEGER NOT NULL,

    -- JSONB for flexible nested data
    ingredients JSONB NOT NULL,
    instructions JSONB NOT NULL,
    shopping_list JSONB NOT NULL,

    -- Original request
    original_prompt TEXT NOT NULL,
    dietary_preferences JSONB,
    cuisine_type VARCHAR(100),

    -- Vector embedding for similarity search (768 dimensions)
    embedding vector(768),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Index for vector similarity search
CREATE INDEX ON recipes USING ivfflat (embedding vector_cosine_ops);
```

### JSONB Examples

**ingredients:**

```json
[
  {
    "name": "Chicken breast",
    "amount": 2,
    "unit": "lbs",
    "aisle": "Meat & Poultry",
    "notes": "boneless, skinless"
  },
  {
    "name": "Olive oil",
    "amount": 2,
    "unit": "tbsp",
    "aisle": "Pantry",
    "notes": null
  }
]
```

**shopping_list:**

```json
{
  "Meat & Poultry": ["2 lbs Chicken breast (boneless, skinless)"],
  "Produce": ["1 medium Onion (diced)", "3 cloves Garlic (minced)"],
  "Pantry": ["2 tbsp Olive oil"]
}
```

### Vector Search

```python
# Find similar recipes using cosine distance
query = (
    select(RecipeDB)
    .where(RecipeDB.embedding.isnot(None))
    .order_by(RecipeDB.embedding.cosine_distance(query_embedding))
    .limit(5)
)
```

---

## API Reference

### Base URL

```
http://localhost:8000/api/recipes
```

### Endpoints

#### Health Check

```http
GET /health
```

Response: `{"status": "healthy", "service": "recipe-generator"}`

#### Generate Recipe

```http
POST /generate
Content-Type: application/json

{
  "prompt": "healthy chicken dinner for 4",
  "dietary_preferences": ["Gluten-Free"],
  "cuisine_type": "Italian"
}
```

Response (201 Created):

```json
{
  "id": "e9bd392b-6f5c-446a-bc99-ca516191748e",
  "recipe": {
    "title": "Italian Herb Grilled Chicken",
    "description": "A light and flavorful chicken dish...",
    "servings": 4,
    "prep_time_minutes": 15,
    "cook_time_minutes": 25,
    "ingredients": [...],
    "instructions": [...]
  },
  "shopping_list": {
    "Meat & Poultry": ["2 lbs Chicken breast"],
    "Produce": ["1 medium Lemon", ...],
    ...
  }
}
```

#### Get Recipe

```http
GET /{recipe_id}
```

#### Find Similar Recipes

```http
GET /{recipe_id}/similar?limit=5
```

#### List Recipes

```http
GET /?limit=20&search=chicken
```

#### Delete Recipe

```http
DELETE /{recipe_id}
```

---

## Development Setup

### Prerequisites

- Python 3.13+
- Node.js 18+
- PostgreSQL 15+ with pgvector extension
- LM Studio with models loaded

### Backend Setup

```bash
cd ai-recipes-generator-backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set up database
createdb recipes
psql -d recipes -c "CREATE EXTENSION vector;"

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd AI-recipes-generator

# Install dependencies
npm install

# Start dev server
npm run dev
```

### LM Studio Setup

1. Download LM Studio from https://lmstudio.ai
2. Load models:
   - Chat: `qwen3-vl-4b-instruct-mlx`
   - Embeddings: `text-embedding-embeddinggemma-300m-qat`
3. Start local server on port 1234

### Environment Variables

**Backend (.env):**

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/recipes
LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
LM_STUDIO_MODEL=qwen3-vl-4b-instruct-mlx
LM_STUDIO_EMBEDDING_MODEL=text-embedding-embeddinggemma-300m-qat
DEBUG=false
```

**Frontend (.env.local):**

```env
RECIPE_API_URL=http://localhost:8000
```

---

## Common Tasks

### Adding a New API Endpoint

1. Add route in `app/api/recipes.py`:

```python
@router.get("/my-endpoint")
async def my_endpoint(...):
    ...
```

2. Add Server Action in `app/actions/recipe.ts`:

```typescript
export async function myAction(): Promise<ActionResult<MyType>> {
  ...
}
```

3. Add TypeScript types in `types/recipe.ts`

### Adding a New Recipe Component

1. Create component in `components/recipe/MyComponent.tsx`
2. Export from `components/recipe/index.ts`
3. Use in pages/forms as needed

### Modifying the AI Prompt

Edit `RECIPE_SYSTEM_PROMPT` in `app/agents/recipe_agent.py`

### Adding a New Database Field

1. Update `RecipeDB` in `app/database/models.py`
2. Update `RecipeRepository` in `app/database/repositories.py`
3. Update Pydantic models in `app/models/recipe.py`
4. Update TypeScript types in `types/recipe.ts`

---

## Troubleshooting

### "Connection is closed" Error

- **Cause:** Database connection timeout during long AI generation
- **Fix:** Already fixed with `pool_pre_ping=True` and fresh session after AI generation

### "LM Studio not responding"

- Ensure LM Studio is running on port 1234
- Check model is loaded and selected

### TypeScript Errors

```bash
npx tsc --noEmit  # Check for type errors
```

### Database Issues

```bash
# Reset database
dropdb recipes && createdb recipes
psql -d recipes -c "CREATE EXTENSION vector;"
# Restart backend to recreate tables
```

---

## Questions?

- Check existing code in `app/agents/` for AI patterns
- Check `app/database/` for DB operations
- Check `components/recipe/` for UI patterns

Happy coding! 🚀
