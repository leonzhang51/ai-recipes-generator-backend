import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import router as api_router
from app.api.recipes import router as recipes_router
from app.core.settings import get_settings
from app.database.connection import init_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    startup_settings = get_settings()
    logger.info(
        "Starting %s v%s",
        startup_settings.project_name,
        startup_settings.version,
    )
    logger.info("LM Studio URL: %s", startup_settings.lm_studio_base_url)
    logger.info("LM Studio Model: %s", startup_settings.lm_studio_model)
    logger.info("Embedding Model: %s", startup_settings.lm_studio_embedding_model)
    logger.info("Debug mode: %s", startup_settings.debug)

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database: %s", e)
        raise

    yield

    # Shutdown
    logger.info("Shutting down application")
    await close_db()
    logger.info("Database connections closed")


# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="AI-powered recipe generator with shopping list functionality",
    lifespan=lifespan,
)

# Include API routes
app.include_router(api_router, prefix="/api")
app.include_router(recipes_router, prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)