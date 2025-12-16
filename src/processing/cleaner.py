"""Data cleaning and preprocessing."""
import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class NewsDataCleaner:
    """Clean and preprocess news articles."""

    def clean_articles(self, articles: list[dict[str, Any]]) -> pd.DataFrame:
        """
        Clean articles data.

        Args:
            articles: List of article dictionaries

        Returns:
            Cleaned pandas DataFrame
        """
        df = pd.DataFrame(articles)

        logger.info(f"Cleaning {len(df)} articles...")

        # Remove articles without content
        df = df.dropna(subset=["content", "title"])

        # Remove duplicates based on title
        df = df.drop_duplicates(subset=["title"], keep="first")

        # Clean text fields
        df["title"] = df["title"].str.strip()
        df["description"] = df["description"].fillna("").str.strip()
        df["content"] = df["content"].str.strip()

        # Parse published date
        df["publishedAt"] = pd.to_datetime(
            df["publishedAt"], errors="coerce"
        )

        # Extract source name
        df["source_name"] = df["source"].apply(
            lambda x: x.get("name", "") if isinstance(x, dict) else ""
        )

        # Select relevant columns
        columns = [
            "title",
            "description",
            "content",
            "url",
            "urlToImage",
            "publishedAt",
            "source_name",
            "author",
        ]

        df = df[columns]

        # Remove articles with removed content
        df = df[~df["content"].str.contains(r"\[.*removed\]", na=False)]

        logger.info(f"Cleaned data: {len(df)} articles remaining")

        return df

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract additional features from articles.

        Args:
            df: DataFrame with articles

        Returns:
            DataFrame with additional features
        """
        # Content length
        df["content_length"] = df["content"].str.len()

        # Word count
        df["word_count"] = df["content"].str.split().str.len()

        # Has image
        df["has_image"] = df["urlToImage"].notna()

        # Day of week
        df["day_of_week"] = df["publishedAt"].dt.day_name()

        # Hour of day
        df["hour"] = df["publishedAt"].dt.hour

        return df
