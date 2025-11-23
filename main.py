"""Application entry point.

This is the main entry point for running the FastAPI application.
"""

if __name__ == "__main__":
    import uvicorn

    from src.config.settings import settings

    uvicorn.run(
        "src.apps.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )
