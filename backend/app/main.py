from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


from app.config import settings
from app.database import engine
from app.routes import auth_router


app = FastAPI(
    title=f"{settings.app_name} API",
    description=(
        "Backend API for the MuseMatch AI music streaming "
        "and recommendation platform."
    ),
    version="1.0.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(auth_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "MuseMatch AI backend is running",
        "status": "success",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "MuseMatch AI API",
        "environment": settings.app_env,
    }


@app.get("/database-health")
def database_health() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "connected",
            "database": settings.database_name,
        }

    except SQLAlchemyError:
        return {
            "status": "disconnected",
            "database": settings.database_name,
        }