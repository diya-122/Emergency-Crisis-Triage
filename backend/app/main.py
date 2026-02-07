"""
Emergency Crisis Triage & Resource Allocation System
Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import db_manager
from app.api.routes import router

# -------------------------------------------------------------------
# Logging Configuration
# -------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Application Lifespan (DB OPTIONAL FOR DEMO)
# -------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
    Database is OPTIONAL for demo reliability.
    """

    logger.info("Starting Emergency Crisis Triage System")

    # Try DB connection (do NOT crash if unavailable)
    try:
        await db_manager.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.warning(
            f"Database not available. Running in demo mode. Reason: {e}"
        )

    yield

    logger.info("Shutting down Emergency Crisis Triage System")

    try:
        await db_manager.disconnect()
    except Exception:
        pass


# -------------------------------------------------------------------
# FastAPI App Initialization
# -------------------------------------------------------------------

app = FastAPI(
    title="Emergency Crisis Triage & Resource Allocation System",
    description="""
AI-powered decision support system for emergency response coordinators.

### Core Capabilities
- Intelligent extraction from unstructured emergency messages
- Explainable urgency scoring with transparent reasoning
- Capability-aware resource matching
- Human-in-the-loop decision support

### Safety & Responsibility
- Human dispatchers retain final authority
- All urgency scores include explanations
- Designed for fairness, transparency, and auditability

### Demo Note
Database connectivity is optional for demo reliability.
""",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# -------------------------------------------------------------------
# CORS Configuration (Required for Netlify frontend)
# -------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# API Routes
# -------------------------------------------------------------------

app.include_router(
    router,
    prefix="/api/v1",
    tags=["Emergency Triage"]
)

# -------------------------------------------------------------------
# Root Health Check
# -------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "system": "Emergency Crisis Triage & Resource Allocation System",
        "version": "1.0.0",
        "status": "operational",
        "mode": "demo-safe",
        "docs": "/docs",
        "api": "/api/v1"
    }

# -------------------------------------------------------------------
# Local Development Entry Point
# -------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
