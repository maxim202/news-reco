"""Load processed data into warehouse."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logging_config import setup_logging
from src.warehouse.connection import DatabaseManager
from src.warehouse.loader import DataWarehouseLoader

logger = setup_logging()


def main():
    """Load data into warehouse."""
    logger.info("Starting data warehouse loading...")

    # Initialize database manager
    db = DatabaseManager()

    try:
        # Connect
        db.connect()

        # Initialize loader
        loader = DataWarehouseLoader(db)

        # Load all processed CSV files
        processed_path = Path("data/processed")
        csv_files = list(processed_path.glob("*_processed.csv"))

        if not csv_files:
            logger.warning("No processed CSV files found!")
            return

        for csv_file in csv_files:
            logger.info(f"\nLoading {csv_file.name}...")
            loader.load_csv_to_warehouse(csv_file)

        # Print statistics
        loader.print_warehouse_stats()

        logger.info("Data loading completed")

    except Exception as e:
        logger.error(f"Loading failed: {e}")
        raise

    finally:
        db.disconnect()


if __name__ == "__main__":
    main()
