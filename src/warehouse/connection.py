"""Database connection manager."""
import logging
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage database connections and operations."""

    def __init__(
        self,
        database_path: str = "data/warehouse.db",
    ):
        """Initialize database manager."""
        self.database_path = database_path
        self.engine: Engine | None = None
        self.SessionLocal = None

    def connect(self) -> Engine:
        """Create database connection."""
        # Create data directory if it doesn't exist
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)

        connection_string = f"sqlite:///{self.database_path}"

        try:
            self.engine = create_engine(
                connection_string,
                echo=False,
                connect_args={"check_same_thread": False},
            )
            self.SessionLocal = sessionmaker(bind=self.engine)

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info(
                    f"✅ Connected to SQLite: {self.database_path}"
                )

            return self.engine

        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            raise

    def disconnect(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Disconnected from database")

    def create_schema(self, schema_file: str) -> None:
        """Create tables from SQL schema file."""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        try:
            with open(schema_file, "r") as f:
                sql_commands = f.read()

            with self.engine.connect() as conn:
                # Split commands by semicolon
                commands = sql_commands.split(";")
                for command in commands:
                    if command.strip():
                        # SQLite doesn't support IF NOT EXISTS in some contexts
                        # but our schema should work fine
                        conn.execute(text(command))
                        logger.info(f"Executed: {command[:50]}...")

                conn.commit()
                logger.info("✅ Schema created successfully")

        except Exception as e:
            logger.error(f"❌ Failed to create schema: {e}")
            raise

    def get_session(self) -> Session:
        """Get database session."""
        if not self.SessionLocal:
            raise RuntimeError("Not connected to database")
        return self.SessionLocal()

    def execute_query(self, query: str) -> list:
        """Execute a SELECT query and return results."""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                return [dict(row._mapping) for row in result.fetchall()]

        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            raise

    def execute_insert(self, query: str, params: dict) -> None:
        """Execute an INSERT query."""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        try:
            with self.engine.connect() as conn:
                conn.execute(text(query), params)
                conn.commit()

        except Exception as e:
            logger.error(f"❌ Insert failed: {e}")
            raise

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        if not self.engine:
            return False

        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(
                        f"SELECT EXISTS (SELECT 1 FROM sqlite_master "
                        f"WHERE type='table' AND name='{table_name}')"
                    )
                )
                return bool(result.scalar())

        except Exception as e:
            logger.error(f"Error checking table: {e}")
            return False

    def get_table_count(self, table_name: str) -> int:
        """Get row count for a table."""
        try:
            result = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
            return result[0]["count"] if result else 0

        except Exception as e:
            logger.error(f"Error getting table count: {e}")
            return 0