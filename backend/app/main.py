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

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for FastAPI app"""
    # Startup
    logger.info("Starting Emergency Crisis Triage System")
    try:
        await db_manager.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Emergency Crisis Triage System")
    await db_manager.disconnect()


# Create FastAPI app
app = FastAPI(
    title="Emergency Crisis Triage & Resource Allocation System",
    description="""
    AI-powered decision support system for emergency response coordinators.
    
    ## Features
    
    * **Intelligent Message Processing**: Extract structured information from unstructured crisis messages
    * **Explainable Urgency Scoring**: Transparent urgency classification with detailed reasoning
    * **Smart Resource Matching**: Multi-factor matching algorithm (suitability, availability, capacity, distance)
    * **Human-in-the-Loop**: All critical decisions require human confirmation
    * **Real-time Dashboard**: Monitor requests, resources, and performance metrics
    
    ## Safety & Ethics
    
    * Human dispatchers maintain final decision authority
    * All urgency scores include detailed explanations
    * System tracks human overrides for continuous learning
    * Designed for fairness, transparency, and accountability
    
    ## Workflow
    
    1. **Receive** unstructured emergency message
    2. **Extract** structured information using LLM
    3. **Calculate** explainable urgency score
    4. **Match** to available resources with trade-off analysis
    5. **Present** recommendations to dispatcher
    6. **Confirm** human decision and dispatch
    
    **Goal**: Reduce triage time by 40% while maintaining safety and transparency.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["Emergency Triage"])


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "system": "Emergency Crisis Triage & Resource Allocation System",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "api": "/api/v1"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
