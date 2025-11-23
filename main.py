"""Application entry point.

This is the main entry point for running the FastAPI application.
"""

if __name__ == "__main__":
    import uvicorn

    from apps.orchestrator.settings import settings

    uvicorn.run(
        "apps.orchestrator.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )
