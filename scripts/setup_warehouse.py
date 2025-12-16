"""Setup and initialize data warehouse."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logging_config import setup_logging
from src.warehouse.connection import DatabaseManager

logger = setup_logging()


def main():
    """Setup warehouse."""
    logger.info("Starting Data Warehouse setup")

    # Initialize database manager with SQLite
    db = DatabaseManager(database_path="data/warehouse.db")

    try:
        # Connect to SQLite
        logger.info("Connecting to SQLite...")
        db.connect()

        # Create schema
        logger.info("Creating schema...")
        schema_file = Path(__file__).parent.parent / "src/warehouse/schema.sql"
        db.create_schema(str(schema_file))

        logger.info("Warehouse setup completed!")

    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise

    finally:
        db.disconnect()


if __name__ == "__main__":
    main()