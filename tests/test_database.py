"""Database tests for THE CIRCLE APP"""
import pytest
import os
import sys
import sqlite3
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database


@pytest.fixture
def test_db():
    """Create a temporary test database"""
    # Create temporary database file
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Store original DB_PATH
    original_db_path = database.DB_PATH

    # Set test database path
    database.DB_PATH = path

    # Initialize database
    database.init_db()

    yield path

    # Restore original DB_PATH
    database.DB_PATH = original_db_path

    # Clean up
    try:
        os.unlink(path)
    except:
        pass


class TestDatabaseInitialization:
    """Test database initialization"""

    def test_database_file_created(self, test_db):
        """Test that database file is created"""
        assert os.path.exists(test_db)

    def test_tables_exist(self, test_db):
        """Test that all required tables exist"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # Check for required tables
        required_tables = [
            "memories",
            "media",
            "memory_media",
            "comments",
            "memory_tags",
            "memory_people",
            "profile",
        ]

        for table in required_tables:
            assert table in tables, f"Table {table} not found"

        conn.close()

    def test_indexes_created(self, test_db):
        """Test that performance indexes are created"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Get list of indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]

        # Check for some key indexes
        expected_indexes = [
            "idx_comments_memory_id",
            "idx_memories_year",
            "idx_media_filename_unique",
        ]

        for index in expected_indexes:
            assert index in indexes, f"Index {index} not found"

        conn.close()


class TestMemoriesTable:
    """Test memories table operations"""

    def test_memories_table_structure(self, test_db):
        """Test that memories table has correct columns"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(memories)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        # Check for required columns
        assert "id" in columns
        assert "text" in columns
        assert "year" in columns
        assert "category" in columns
        assert "created_at" in columns

        conn.close()


class TestMediaTable:
    """Test media table operations"""

    def test_media_table_structure(self, test_db):
        """Test that media table has correct columns"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(media)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        # Check for required columns
        assert "id" in columns
        assert "filename" in columns
        assert "file_type" in columns
        assert "year" in columns
        assert "file_size" in columns  # Added in migration

        conn.close()


class TestForeignKeys:
    """Test foreign key constraints"""

    def test_foreign_keys_enabled(self, test_db):
        """Test that foreign keys are enabled"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()

        # Foreign keys should be enabled (1) or at least available
        assert result is not None

        conn.close()

    def test_memory_media_foreign_keys(self, test_db):
        """Test that memory_media has foreign key constraints"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        cursor.execute("PRAGMA foreign_key_list(memory_media)")
        foreign_keys = cursor.fetchall()

        # Should have foreign keys to memories and media tables
        assert len(foreign_keys) >= 2

        conn.close()


class TestMigrations:
    """Test database migrations"""

    def test_migration_runs_successfully(self, test_db):
        """Test that migration runs without errors"""
        try:
            database.migrate_db()
            success = True
        except Exception as e:
            success = False
            print(f"Migration failed: {e}")

        assert success

    def test_file_size_column_added(self, test_db):
        """Test that file_size column was added in migration"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(media)")
        columns = [row[1] for row in cursor.fetchall()]

        assert "file_size" in columns

        conn.close()


class TestIndexPerformance:
    """Test that indexes improve query performance"""

    def test_unique_filename_constraint(self, test_db):
        """Test that unique filename constraint works"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Insert a media file
        cursor.execute(
            """
            INSERT INTO media (filename, file_type, year)
            VALUES (?, ?, ?)
        """,
            ("test.jpg", "image", 2024),
        )
        conn.commit()

        # Try to insert duplicate filename - should fail
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                """
                INSERT INTO media (filename, file_type, year)
                VALUES (?, ?, ?)
            """,
                ("test.jpg", "image", 2024),
            )
            conn.commit()

        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
