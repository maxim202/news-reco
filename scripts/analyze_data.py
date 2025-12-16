"""Analyze processed news data."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logging_config import setup_logging

logger = setup_logging()


def main():
    """Analyze processed data."""
    processed_data_path = Path("data/processed")

    logger.info("Analyzing processed data...")

    for csv_file in processed_data_path.glob("*_processed.csv"):

        logger.info(f"File: {csv_file.name}")


        df = pd.read_csv(csv_file)

        # Basic info
        logger.info(f"\nShape: {df.shape[0]} rows, {df.shape[1]} columns")

        # Columns
        logger.info(f"\nColumns: {list(df.columns)}")

        # Data types
        logger.info(f"\nData Types:\n{df.dtypes}")

        # Missing values
        logger.info(f"\nMissing Values:\n{df.isnull().sum()}")

        # Statistics for numeric columns
        logger.info(f"\nStatistics for numeric columns:\n{df.describe()}")

        # Day of week distribution
        if "day_of_week" in df.columns:
            logger.info(
                f"\nArticles by Day of Week:\n{df['day_of_week'].value_counts()}"
            )

        # Has image distribution
        if "has_image" in df.columns:
            logger.info(
                f"\nArticles with Image: {df['has_image'].sum()} / {len(df)}"
            )

        # Content length stats
        if "content_length" in df.columns:
            logger.info(
                f"\nContent Length - Min: {df['content_length'].min()}, "
                f"Max: {df['content_length'].max()}, "
                f"Mean: {df['content_length'].mean():.0f}"
            )


if __name__ == "__main__":
    main()