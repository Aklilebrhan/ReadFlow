from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import setup_exception_handlers
from app.shared.database.session import init_db

# Modules
from app.modules.documents.router import router as documents_router
from app.modules.chat.router import router as chat_router
from app.modules.summaries.router import router as summaries_router
from app.modules.explanation.router import router as explanation_router
from app.modules.study.router import router as study_router

setup_logging()
logger = get_logger("readflow.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up ReadFlow API service...")
    await init_db()
    yield
    logger.info("Shutting down ReadFlow API service...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ReadFlow: AI-Powered Document Intelligence Platform API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
setup_exception_handlers(app)

# Mount Routers
api_v1 = settings.API_V1_PREFIX
app.include_router(documents_router, prefix=api_v1)
app.include_router(chat_router, prefix=api_v1)
app.include_router(summaries_router, prefix=api_v1)
app.include_router(explanation_router, prefix=api_v1)
app.include_router(study_router, prefix=api_v1)


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "ai_provider": settings.AI_PROVIDER,
        "storage_provider": settings.STORAGE_PROVIDER
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} Document Intelligence API",
        "docs": "/docs",
        "version": settings.APP_VERSION,
        "health": "/health"
    }
