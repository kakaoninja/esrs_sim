"""Database connection management for SQLite.

Provides connection pooling, transaction management, and resource cleanup
for the master_climate_sim.db SQLite database.

Database location: data/master_climate_sim.db
"""

import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


class DatabaseConnection:
    """Singleton database connection manager for SQLite.

    Manages SQLite connections with proper resource cleanup and
    transaction handling. Ensures foreign key constraints are enabled.

    Attributes:
        db_path: Path to SQLite database file
        _connection: Active SQLite connection (if any)
    """

    _instance: Optional['DatabaseConnection'] = None
    _connection: Optional[sqlite3.Connection] = None

    def __new__(cls, db_path: Optional[str] = None):
        """Ensure singleton pattern for database connections.

        Args:
            db_path: Path to database file (only used on first instantiation)

        Returns:
            DatabaseConnection singleton instance
        """
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            if db_path is None:
                # Default path: data/master_climate_sim.db relative to project root
                project_root = Path(__file__).parent.parent.parent
                db_path = str(project_root / "data" / "master_climate_sim.db")
            cls._instance.db_path = db_path
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        """Get active SQLite connection, creating if needed.

        Enables foreign key constraints and row factory for dict-like access.

        Returns:
            Active SQLite connection

        Raises:
            FileNotFoundError: If database file does not exist
        """
        if self._connection is None:
            db_file = Path(self.db_path)
            if not db_file.exists():
                raise FileNotFoundError(f"Database file not found: {self.db_path}")

            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row  # Enable dict-like access to rows
            self._connection.execute("PRAGMA foreign_keys = ON")  # Enable FK constraints
            self._connection.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging for performance

        return self._connection

    def close(self):
        """Close database connection and cleanup resources."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    @contextmanager
    def transaction(self):
        """Context manager for database transactions with automatic commit/rollback.

        Usage:
            with db.transaction():
                cursor.execute("INSERT INTO ...")
                # Automatically commits on success, rolls back on exception

        Yields:
            SQLite connection within transaction context

        Raises:
            Any exception from transaction operations (connection is rolled back)
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e

    def execute_query(self, query: str, parameters: tuple = ()) -> list[sqlite3.Row]:
        """Execute SELECT query and return all results.

        Args:
            query: SQL SELECT query string
            parameters: Query parameters tuple (for parameterized queries)

        Returns:
            List of sqlite3.Row objects (dict-like access)

        Raises:
            sqlite3.Error: On database errors
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        return cursor.fetchall()

    def execute_insert(self, query: str, parameters: tuple = ()) -> int:
        """Execute INSERT query and return last row ID.

        Args:
            query: SQL INSERT query string
            parameters: Query parameters tuple

        Returns:
            Last inserted row ID

        Raises:
            sqlite3.Error: On database errors
        """
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, parameters)
            return cursor.lastrowid

    def execute_update(self, query: str, parameters: tuple = ()) -> int:
        """Execute UPDATE query and return number of affected rows.

        Args:
            query: SQL UPDATE query string
            parameters: Query parameters tuple

        Returns:
            Number of rows affected

        Raises:
            sqlite3.Error: On database errors
        """
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, parameters)
            return cursor.rowcount

    def execute_delete(self, query: str, parameters: tuple = ()) -> int:
        """Execute DELETE query and return number of deleted rows.

        Args:
            query: SQL DELETE query string
            parameters: Query parameters tuple

        Returns:
            Number of rows deleted

        Raises:
            sqlite3.Error: On database errors
        """
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, parameters)
            return cursor.rowcount

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database.

        Args:
            table_name: Name of table to check

        Returns:
            True if table exists, False otherwise
        """
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
        """
        results = self.execute_query(query, (table_name,))
        return len(results) > 0

    def get_table_row_count(self, table_name: str) -> int:
        """Get row count for a table.

        Args:
            table_name: Name of table to count

        Returns:
            Number of rows in table

        Raises:
            sqlite3.Error: If table does not exist
        """
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        results = self.execute_query(query)
        return results[0]['count']

    def __del__(self):
        """Cleanup connection on object destruction."""
        self.close()


# Convenience function for getting database connection
def get_db() -> DatabaseConnection:
    """Get the singleton database connection instance.

    Returns:
        DatabaseConnection singleton

    Example:
        db = get_db()
        results = db.execute_query("SELECT * FROM company_profiles WHERE company_id = ?", ("TEST_001",))
    """
    return DatabaseConnection()
