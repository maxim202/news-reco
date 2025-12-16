"""Load processed data into data warehouse."""
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd
from sqlalchemy import text

from src.warehouse.connection import DatabaseManager

logger = logging.getLogger(__name__)


class DataWarehouseLoader:
    """Load data from CSV into SQLite warehouse."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize loader."""
        self.db = db_manager

    def load_csv_to_warehouse(self, csv_file: Path) -> None:
        """Load CSV data into warehouse."""
        logger.info(f"Loading data from {csv_file.name}...")

        # Read CSV
        df = pd.read_csv(csv_file)
        logger.info(f"Loaded {len(df)} articles from CSV")

        # Load dimensions and fact table
        self._load_dimensions(df)
        self._load_fact_table(df)

        logger.info("✅ Data loading completed")

    def _load_dimensions(self, df: pd.DataFrame) -> None:
        """Load dimension tables."""
        logger.info("Loading dimension tables...")

        # Load dim_source
        self._load_dim_source(df)

        # Load dim_author
        self._load_dim_author(df)

        # Load dim_time
        self._load_dim_time(df)

    def _load_dim_source(self, df: pd.DataFrame) -> None:
        """Load source dimension."""
        sources = df["source_name"].unique()
        count = 0

        for source in sources:
            if pd.isna(source) or source == "":
                continue

            try:
                query = """
                    INSERT INTO dim_source (source_name)
                    VALUES (:source_name)
                """
                self.db.execute_insert(
                    query, {"source_name": str(source)}
                )
                count += 1
            except Exception as e:
                logger.warning(f"Could not insert source {source}: {e}")

        logger.info(f"✅ Loaded {count} sources to dim_source")

    def _load_dim_author(self, df: pd.DataFrame) -> None:
        """Load author dimension."""
        authors = df["author"].dropna().unique()
        count = 0

        for author in authors:
            try:
                query = """
                    INSERT INTO dim_author (author_name)
                    VALUES (:author_name)
                """
                self.db.execute_insert(
                    query, {"author_name": str(author)}
                )
                count += 1
            except Exception as e:
                logger.warning(f"Could not insert author {author}: {e}")

        logger.info(f"✅ Loaded {count} authors to dim_author")

    def _load_dim_time(self, df: pd.DataFrame) -> None:
        """Load time dimension."""
        dates = pd.to_datetime(df["publishedAt"]).dt.date.unique()
        count = 0

        for date in dates:
            try:
                date_obj = pd.Timestamp(date)
                query = """
                    INSERT INTO dim_time 
                    (date, year, month, day, day_of_week, 
                     week_of_year, quarter, is_weekend)
                    VALUES (:date, :year, :month, :day, :day_of_week,
                            :week_of_year, :quarter, :is_weekend)
                """
                self.db.execute_insert(
                    query,
                    {
                        "date": str(date),
                        "year": date_obj.year,
                        "month": date_obj.month,
                        "day": date_obj.day,
                        "day_of_week": date_obj.day_name(),
                        "week_of_year": date_obj.isocalendar()[1],
                        "quarter": (date_obj.month - 1) // 3 + 1,
                        "is_weekend": 1 if date_obj.weekday() >= 5 else 0,
                    },
                )
                count += 1
            except Exception as e:
                logger.warning(f"Could not insert date {date}: {e}")

        logger.info(f"✅ Loaded {count} dates to dim_time")

    def _load_fact_table(self, df: pd.DataFrame) -> None:
        """Load fact table with articles."""
        logger.info("Loading fact_articles table...")
        count = 0

        for idx, row in df.iterrows():
            try:
                # Get IDs from dimensions
                source_id = self._get_source_id(row["source_name"])
                author_id = self._get_author_id(row.get("author"))
                time_id = self._get_time_id(row["publishedAt"])

                query = """
                    INSERT INTO fact_articles
                    (title, description, content, url, image_url,
                     source_id, author_id, published_time_id,
                     content_length, word_count, has_image)
                    VALUES
                    (:title, :description, :content, :url, :image_url,
                     :source_id, :author_id, :published_time_id,
                     :content_length, :word_count, :has_image)
                """

                self.db.execute_insert(
                    query,
                    {
                        "title": row["title"],
                        "description": row["description"] or None,
                        "content": row["content"],
                        "url": row["url"],
                        "image_url": row.get("urlToImage") or None,
                        "source_id": source_id,
                        "author_id": author_id,
                        "published_time_id": time_id,
                        "content_length": int(row["content_length"]),
                        "word_count": int(row["word_count"]),
                        "has_image": 1 if row["has_image"] else 0,
                    },
                )
                count += 1

            except Exception as e:
                logger.warning(
                    f"Could not insert article {row['title'][:50]}: {e}"
                )

        logger.info(f"✅ Loaded {count} articles to fact_articles")

    def _get_source_id(self, source_name: str) -> int:
        """Get source ID."""
        if pd.isna(source_name) or source_name == "":
            return None

        try:
            # Escape single quotes in source name
            safe_name = str(source_name).replace("'", "''")
            query = (
                f"SELECT source_id FROM dim_source "
                f"WHERE source_name = '{safe_name}'"
            )
            result = self.db.execute_query(query)
            return result[0]["source_id"] if result else None
        except Exception as e:
            logger.warning(f"Could not get source_id: {e}")
            return None

    def _get_author_id(self, author_name: str) -> int:
        """Get author ID."""
        if pd.isna(author_name) or author_name == "":
            return None

        try:
            # Escape single quotes in author name
            safe_name = str(author_name).replace("'", "''")
            query = (
                f"SELECT author_id FROM dim_author "
                f"WHERE author_name = '{safe_name}'"
            )
            result = self.db.execute_query(query)
            return result[0]["author_id"] if result else None
        except Exception as e:
            logger.warning(f"Could not get author_id: {e}")
            return None

    def _get_time_id(self, published_at: str) -> int:
        """Get time ID."""
        try:
            date = pd.to_datetime(published_at).date()
            query = (
                f"SELECT time_id FROM dim_time "
                f"WHERE date = '{date}'"
            )
            result = self.db.execute_query(query)
            return result[0]["time_id"] if result else None
        except Exception as e:
            logger.warning(f"Could not get time_id: {e}")
            return None

    def print_warehouse_stats(self) -> None:
        """Print warehouse statistics."""
        logger.info("\n" + "=" * 60)
        logger.info("📊 DATA WAREHOUSE STATISTICS")
        logger.info("=" * 60)

        tables = [
            "dim_time",
            "dim_source",
            "dim_author",
            "fact_articles",
        ]

        for table in tables:
            count = self.db.get_table_count(table)
            logger.info(f"  {table}: {count} rows")

        logger.info("=" * 60 + "\n")