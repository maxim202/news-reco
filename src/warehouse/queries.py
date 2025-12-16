"""Common SQL queries for analysis."""
import logging

from src.warehouse.connection import DatabaseManager

logger = logging.getLogger(__name__)


class WarehouseQueries:
    """Execute analytical queries on warehouse."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize queries."""
        self.db = db_manager

    def get_articles_by_source(self) -> list:
        """Get article count by source."""
        query = """
            SELECT 
                s.source_name,
                COUNT(f.article_id) as article_count,
                AVG(f.word_count) as avg_word_count,
                AVG(f.content_length) as avg_content_length
            FROM fact_articles f
            JOIN dim_source s ON f.source_id = s.source_id
            GROUP BY s.source_name
            ORDER BY article_count DESC
        """
        return self.db.execute_query(query)

    def get_articles_by_day_of_week(self) -> list:
        """Get article distribution by day of week."""
        query = """
            SELECT 
                t.day_of_week,
                COUNT(f.article_id) as article_count,
                SUM(CASE WHEN f.has_image THEN 1 ELSE 0 END) as articles_with_image
            FROM fact_articles f
            JOIN dim_time t ON f.published_time_id = t.time_id
            GROUP BY t.day_of_week
            ORDER BY t.day_of_week
        """
        return self.db.execute_query(query)

    def get_articles_by_author(self, limit: int = 10) -> list:
        """Get top authors by article count."""
        query = f"""
            SELECT 
                a.author_name,
                COUNT(f.article_id) as article_count,
                AVG(f.word_count) as avg_word_count
            FROM fact_articles f
            JOIN dim_author a ON f.author_id = a.author_id
            WHERE a.author_name IS NOT NULL
            GROUP BY a.author_name
            ORDER BY article_count DESC
            LIMIT {limit}
        """
        return self.db.execute_query(query)

    def get_articles_with_images_stats(self) -> list:
        """Get statistics about articles with images."""
        query = """
            SELECT 
                has_image,
                COUNT(*) as article_count,
                AVG(word_count) as avg_word_count,
                AVG(content_length) as avg_content_length
            FROM fact_articles
            GROUP BY has_image
        """
        return self.db.execute_query(query)

    def get_content_length_distribution(self) -> list:
        """Get distribution of content lengths."""
        query = """
            SELECT 
                CASE 
                    WHEN word_count < 100 THEN 'Very Short'
                    WHEN word_count < 300 THEN 'Short'
                    WHEN word_count < 600 THEN 'Medium'
                    WHEN word_count < 1000 THEN 'Long'
                    ELSE 'Very Long'
                END as content_category,
                COUNT(*) as article_count,
                ROUND(AVG(word_count), 0) as avg_words,
                ROUND(AVG(content_length), 0) as avg_chars
            FROM fact_articles
            GROUP BY content_category
            ORDER BY avg_words
        """
        return self.db.execute_query(query)

    def get_top_articles_by_length(self, limit: int = 5) -> list:
        """Get longest articles."""
        query = f"""
            SELECT 
                f.title,
                s.source_name,
                a.author_name,
                f.word_count,
                f.content_length,
                t.date
            FROM fact_articles f
            LEFT JOIN dim_source s ON f.source_id = s.source_id
            LEFT JOIN dim_author a ON f.author_id = a.author_id
            LEFT JOIN dim_time t ON f.published_time_id = t.time_id
            ORDER BY f.word_count DESC
            LIMIT {limit}
        """
        return self.db.execute_query(query)

    def get_warehouse_summary(self) -> dict:
        """Get overall warehouse summary."""
        query = """
            SELECT 
                COUNT(DISTINCT article_id) as total_articles,
                COUNT(DISTINCT source_id) as total_sources,
                COUNT(DISTINCT author_id) as total_authors,
                ROUND(AVG(word_count), 0) as avg_word_count,
                ROUND(AVG(content_length), 0) as avg_content_length,
                SUM(CASE WHEN has_image THEN 1 ELSE 0 END) as articles_with_image
            FROM fact_articles
        """
        result = self.db.execute_query(query)
        return result[0] if result else {}
