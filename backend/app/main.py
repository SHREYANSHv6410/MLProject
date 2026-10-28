import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.models.registry import registry
from backend.app.api.endpoints import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("replysense")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing ReplySense database...")
    init_db()
    logger.info("Attempting to load ML model artifact...")
    try:
        registry.load()
        if registry.is_ready():
            logger.info("ML model and explainer successfully loaded into memory.")
        else:
            logger.warning("No trained ML model found at %s. Please run training script.", settings.MODEL_PATH)
    except Exception as e:
        logger.error("Error loading model: %s", str(e))
    yield
    # Shutdown
    logger.info("ReplySense shutting down.")


app = FastAPI(
    title="ReplySense API",
    description="Statistical Chat Reply Prediction System with Calibrated Probabilities and Explainability",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to ReplySense API",
        "tagline": "Understand the patterns behind every unanswered message.",
        "docs_url": "/docs",
        "health_url": f"{settings.API_PREFIX}/health",
        "model_loaded": registry.is_ready()
    }
