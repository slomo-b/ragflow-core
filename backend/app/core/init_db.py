import logging
from sqlalchemy.orm import Session

from .database import SessionLocal, create_tables
from ..models.collection import Collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with tables and default data"""
    logger.info("Creating database tables...")
    create_tables()
    
    logger.info("Adding default data...")
    db = SessionLocal()
    try:
        # Create default collection if it doesn't exist
        default_collection = db.query(Collection).filter(
            Collection.name == "Default Collection"
        ).first()
        
        if not default_collection:
            default_collection = Collection(
                name="Default Collection",
                description="Default collection for uploaded documents"
            )
            db.add(default_collection)
            db.commit()
            logger.info("Default collection created")
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
