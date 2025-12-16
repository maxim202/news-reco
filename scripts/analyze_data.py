"""Analyze data warehouse."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logging_config import setup_logging
from src.warehouse.connection import DatabaseManager
from src.warehouse.queries import WarehouseQueries

logger = setup_logging()


def print_table(data: list, title: str) -> None:
    """Print results as table."""
    if not data:
        logger.info(f"No data for {title}")
        return

    logger.info(f"\n{title}")
    logger.info("=" * 80)

    # Get column names
    columns = list(data[0].keys())

    # Print header
    header = " | ".join(f"{col:20}" for col in columns)
    logger.info(header)


    # Print rows
    for row in data:
        values = [
            str(row[col])[:20].ljust(20) for col in columns
        ]
        logger.info(" | ".join(values))




def main():
    """Analyze warehouse."""
    logger.info("Starting Data Warehouse Analysis...\n")

    db = DatabaseManager()

    try:
        db.connect()
        queries = WarehouseQueries(db)

        # Summary
        summary = queries.get_warehouse_summary()
        logger.info("\nWAREHOUSE SUMMARY")
    
        for key, value in summary.items():
            logger.info(f"  {key}: {value}")

        # Articles by source
        data = queries.get_articles_by_source()
        print_table(data, "Articles by Source")

        # Articles by day of week
        data = queries.get_articles_by_day_of_week()
        print_table(data, "Articles by Day of Week")

        # Top authors
        data = queries.get_articles_by_author(limit=5)
        print_table(data, "Top 5 Authors by Article Count")

        # Images statistics
        data = queries.get_articles_with_images_stats()
        print_table(data, "Articles with/without Images")

        # Content length distribution
        data = queries.get_content_length_distribution()
        print_table(data, "Content Length Distribution")

        # Top longest articles
        data = queries.get_top_articles_by_length(limit=3)
        print_table(data, "Top 3 Longest Articles")

        logger.info("\nAnalysis completed!")

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise

    finally:
        db.disconnect()


if __name__ == "__main__":
    main()