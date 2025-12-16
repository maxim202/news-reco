"""Process raw news data."""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logging_config import setup_logging
from src.processing.cleaner import NewsDataCleaner

logger = setup_logging()


def main():
    """Process all raw news files."""
    logger.info("Starting data processing...")

    raw_data_path = Path("data/raw")
    processed_data_path = Path("data/processed")
    processed_data_path.mkdir(exist_ok=True)

    cleaner = NewsDataCleaner()

    # Process raw data 
    for json_file in raw_data_path.glob("*.json"):
        logger.info(f"Processing {json_file.name}...")

        # Load raw data
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        articles = data.get("articles", [])

        if not articles:
            logger.warning(f"No articles found in {json_file.name}")
            continue

        # Clean data
        df = cleaner.clean_articles(articles)

        # Extract features
        df = cleaner.extract_features(df)

        # Save processed data
        output_file = (
            processed_data_path / f"{json_file.stem}_processed.csv"
        )
        df.to_csv(output_file, index=False, encoding="utf-8")

        logger.info(f"Saved processed data to {output_file}")
        logger.info(f"Shape: {df.shape}")

    logger.info("Data processing completed!")


if __name__ == "__main__":
    main()