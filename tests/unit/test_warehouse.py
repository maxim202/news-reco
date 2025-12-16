"""Unit tests for data warehouse."""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from src.warehouse.connection import DatabaseManager
from src.warehouse.loader import DataWarehouseLoader
from src.warehouse.queries import WarehouseQueries


class TestDatabaseManager:
    """Test DatabaseManager class."""

    def test_init(self):
        """Test initialization."""
        db = DatabaseManager(database_path="test_warehouse.db")

        assert db.database_path == "test_warehouse.db"

    def test_connection_string_format(self):
        """Test connection string format."""
        db = DatabaseManager(database_path="data/warehouse.db")

        # SQLite connection string format
        assert "warehouse.db" in db.database_path
        assert db.engine is None  # Not connected yet


class TestDataWarehouseLoader:
    """Test DataWarehouseLoader class."""

    def test_init(self):
        """Test loader initialization."""
        mock_db = MagicMock()
        loader = DataWarehouseLoader(mock_db)

        assert loader.db == mock_db

    @patch("pandas.read_csv")
    def test_load_csv_to_warehouse(self, mock_read_csv):
        """Test CSV loading."""
        import pandas as pd

        # Mock data
        mock_df = pd.DataFrame({
            "title": ["Article 1", "Article 2"],
            "description": ["Desc 1", "Desc 2"],
            "content": ["Content 1", "Content 2"],
            "url": ["http://example.com/1", "http://example.com/2"],
            "urlToImage": ["img1.jpg", "img2.jpg"],
            "source_name": ["Source A", "Source B"],
            "author": ["Author 1", "Author 2"],
            "publishedAt": ["2024-01-01", "2024-01-02"],
            "content_length": [100, 200],
            "word_count": [10, 20],
            "has_image": [True, True],
        })

        mock_read_csv.return_value = mock_df

        mock_db = MagicMock()
        loader = DataWarehouseLoader(mock_db)

        from pathlib import Path
        loader.load_csv_to_warehouse(Path("dummy.csv"))

        # Verify CSV was read
        mock_read_csv.assert_called_once()


class TestWarehouseQueries:
    """Test WarehouseQueries class."""

    def test_init(self):
        """Test queries initialization."""
        mock_db = MagicMock()
        queries = WarehouseQueries(mock_db)

        assert queries.db == mock_db

    def test_get_articles_by_source_query_format(self):
        """Test query format for articles by source."""
        mock_db = MagicMock()
        mock_db.execute_query.return_value = [
            {
                "source_name": "Test Source",
                "article_count": 10,
                "avg_word_count": 500.0,
                "avg_content_length": 3000.0,
            }
        ]

        queries = WarehouseQueries(mock_db)
        result = queries.get_articles_by_source()

        # Verify execute_query was called
        mock_db.execute_query.assert_called_once()

        # Verify result format
        assert len(result) == 1
        assert result[0]["source_name"] == "Test Source"
        assert result[0]["article_count"] == 10

    def test_get_articles_by_day_of_week_query_format(self):
        """Test query format for articles by day."""
        mock_db = MagicMock()
        mock_db.execute_query.return_value = [
            {
                "day_of_week": "Monday",
                "article_count": 15,
                "articles_with_image": 10,
            }
        ]

        queries = WarehouseQueries(mock_db)
        result = queries.get_articles_by_day_of_week()

        assert len(result) == 1
        assert "day_of_week" in result[0]
        assert "article_count" in result[0]

    def test_get_warehouse_summary_query_format(self):
        """Test warehouse summary query format."""
        mock_db = MagicMock()
        mock_db.execute_query.return_value = [
            {
                "total_articles": 100,
                "total_sources": 5,
                "total_authors": 50,
                "avg_word_count": 450,
                "avg_content_length": 2800,
                "articles_with_image": 80,
            }
        ]

        queries = WarehouseQueries(mock_db)
        result = queries.get_warehouse_summary()

        assert result["total_articles"] == 100
        assert result["total_sources"] == 5
        assert result["articles_with_image"] == 80

    def test_get_articles_by_author_query_format(self):
        """Test top authors query format."""
        mock_db = MagicMock()
        mock_db.execute_query.return_value = [
            {
                "author_name": "Test Author",
                "article_count": 20,
                "avg_word_count": 500.0,
            }
        ]

        queries = WarehouseQueries(mock_db)
        result = queries.get_articles_by_author(limit=5)

        assert len(result) >= 1
        assert "author_name" in result[0]

    def test_get_articles_with_images_stats_query_format(self):
        """Test images statistics query."""
        mock_db = MagicMock()
        mock_db.execute_query.return_value = [
            {
                "has_image": True,
                "article_count": 80,
                "avg_word_count": 500.0,
                "avg_content_length": 3000.0,
            }
        ]

        queries = WarehouseQueries(mock_db)
        result = queries.get_articles_with_images_stats()

        assert len(result) >= 1
        assert "has_image" in result[0]
        assert "article_count" in result[0]