"""
Lexi - AI-Powered Language Adventure Bot
Main FastAPI application entry point
"""

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# from app.database import load_language_data
from app.adapters.redis_cache import RedisCache
from app.database import session_maker
from app.settings import get_settings
from app.telegram.bot import bot, start_bot, start_listening_for_updates

# Configure loguru to output to stdout
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time} | {level} | {message}")


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Load language data from database
    try:
        # supported_languages, supported_languages_in_user_language = await load_language_data()
        # settings = get_settings()
        # settings.language.supported_languages = supported_languages
        # settings.language.supported_languages_in_user_language = (
        #    supported_languages_in_user_language
        # )
        logger.info("Language data loaded from database successfully")
    except Exception as e:
        logger.error(f"Failed to load language data from database: {e}")
        # Fallback to empty dictionaries if database is not available
        settings = get_settings()
        settings.language.supported_languages = {}
        settings.language.supported_languages_in_user_language = {}

    # Initialize Redis cache
    settings = get_settings()
    redis_cache = RedisCache(settings.redis_url)
    await redis_cache.connect()

    polling_task = await start_listening_for_updates()
    await start_bot(redis_cache, session_maker)
    yield
    if polling_task:
        polling_task.cancel()
    await bot.close()
    await redis_cache.disconnect()


app = FastAPI(
    title="Lexi - AI Language Adventure Bot",
    description="An AI-powered bot for interactive storytelling to teach kids foreign languages",
    version="1.0.0",
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Welcome to Lexi - AI Language Adventure Bot!",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
