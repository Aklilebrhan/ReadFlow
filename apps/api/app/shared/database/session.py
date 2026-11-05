import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.core.logging import get_logger
from app.shared.database.base import Base

logger = get_logger(__name__)

# Ensure sqlite data directory exists if using local sqlite fallback
if settings.DATABASE_URL.startswith("sqlite"):
    db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    if db_path.startswith("./") or "/" in db_path:
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

# Create Async Engine
engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    **engine_kwargs
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for yielding an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initializes database schema and extensions."""
    logger.info("Initializing database with URL: %s", settings.DATABASE_URL.split("@")[-1])

    async with engine.begin() as conn:
        # If postgres, enable pgvector extension
        if "postgresql" in settings.DATABASE_URL:
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                logger.info("PostgreSQL vector extension verified or created.")
            except Exception as e:
                logger.warning("Could not enable pgvector extension: %s", str(e))

        # Create tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema synchronized successfully.")
