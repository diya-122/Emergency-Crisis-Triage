"""
Database initialization and connection management
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.models.schemas import EmergencyRequest, Resource
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MongoDB connection and initialization"""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB and initialize Beanie ODM"""
        try:
            logger.info(f"Connecting to MongoDB at {settings.mongodb_url}")
            self.client = AsyncIOMotorClient(settings.mongodb_url)
            self.db = self.client[settings.mongodb_db_name]
            
            # Initialize Beanie with document models
            await init_beanie(
                database=self.db,
                document_models=[EmergencyRequest, Resource]
            )
            
            logger.info("Successfully connected to MongoDB")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def _create_indexes(self):
        """Create necessary database indexes"""
        try:
            # Additional custom indexes can be created here
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def health_check(self) -> bool:
        """Check if database connection is healthy"""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


async def get_database():
    """Dependency for FastAPI routes"""
    return db_manager.db
