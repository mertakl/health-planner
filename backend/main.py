import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import routes
from backend.config import get_settings
from backend.db.session import create_db_and_tables

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info(f"Starting {settings.APP_NAME}")
    logging.info(f"Debug mode: {settings.DEBUG}")

    # Migrate tables on startup
    create_db_and_tables()

    yield

    # Shutdown
    logging.info(f"Shutting down {settings.APP_NAME}")


# App
app = FastAPI(
    title=settings.APP_NAME,
    description="Personalized health and fitness planning",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(routes.router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
