# database.py - Database setup and connection
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "circle_memories.db")


def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with all tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table for authentication
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        is_admin BOOLEAN DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT,
        last_login TEXT
    )"""
    )

    # User profile
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        birth_date TEXT,
        family_role TEXT,
        birth_place TEXT,
        created_at TEXT
    )"""
    )

    # Memories
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        category TEXT,
        memory_date TEXT,
        year INTEGER,
        people TEXT,
        places TEXT,
        created_at TEXT
    )"""
    )

    # Media - FIXED: Added file_size column
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_filename TEXT,
        file_type TEXT,
        file_size INTEGER,
        title TEXT,
        description TEXT,
        memory_date TEXT,
        year INTEGER,
        people TEXT,
        uploaded_by TEXT,
        created_at TEXT
    )"""
    )

    # Comments (Love notes)
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory_id INTEGER,
        author_name TEXT,
        author_relation TEXT,
        comment_text TEXT,
        created_at TEXT,
        FOREIGN KEY (memory_id) REFERENCES memories(id)
    )"""
    )

    # Audio transcriptions
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS audio_transcriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audio_filename TEXT,
        transcription_text TEXT,
        confidence REAL,
        created_at TEXT
    )"""
    )

    # Tags for enhanced search
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS memory_tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory_id INTEGER,
        tag TEXT,
        FOREIGN KEY (memory_id) REFERENCES memories(id)
    )"""
    )

    # People mentioned
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS memory_people (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory_id INTEGER,
        person_name TEXT,
        FOREIGN KEY (memory_id) REFERENCES memories(id)
    )"""
    )

    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")


def migrate_db():
    """Add file_size column, users table, and database indexes if they don't exist."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if file_size column exists
        cursor.execute("PRAGMA table_info(media)")
        columns = [row[1] for row in cursor.fetchall()]

        if "file_size" not in columns:
            cursor.execute("ALTER TABLE media ADD COLUMN file_size INTEGER")
            conn.commit()
            print("✓ Added file_size column to media table")

        # Check if users table exists (for authentication)
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='users'
        """)
        if not cursor.fetchone():
            cursor.execute('''CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                is_admin BOOLEAN DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT,
                last_login TEXT
            )''')
            conn.commit()
            print("✓ Created users table for authentication")

        # Add performance indexes
        add_database_indexes(cursor)
        conn.commit()

        conn.close()
    except Exception as e:
        print(f"Migration error: {e}")


def add_database_indexes(cursor):
    """Add database indexes for improved query performance."""
    indexes = [
        # Users table indexes for authentication
        ("idx_users_username", "users", "username"),
        ("idx_users_email", "users", "email"),
        ("idx_users_active", "users", "is_active"),
        # Foreign key indexes for faster joins
        ("idx_comments_memory_id", "comments", "memory_id"),
        ("idx_memory_tags_memory_id", "memory_tags", "memory_id"),
        ("idx_memory_people_memory_id", "memory_people", "memory_id"),
        ("idx_memory_media_memory_id", "memory_media", "memory_id"),
        ("idx_memory_media_media_id", "memory_media", "media_id"),
        # Search optimization indexes
        ("idx_memories_year", "memories", "year"),
        ("idx_memories_category", "memories", "category"),
        ("idx_media_year", "media", "year"),
        ("idx_media_file_type", "media", "file_type"),
        # Unique constraint on media filename (prevent duplicates)
        ("idx_media_filename_unique", "media", "filename"),
    ]

    created_count = 0
    for index_name, table_name, column_name in indexes:
        try:
            # Check if index already exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
                (index_name,),
            )
            if not cursor.fetchone():
                # Create index (use UNIQUE for filename)
                if "unique" in index_name:
                    cursor.execute(
                        f"CREATE UNIQUE INDEX {index_name} ON {table_name}({column_name})"
                    )
                else:
                    cursor.execute(
                        f"CREATE INDEX {index_name} ON {table_name}({column_name})"
                    )
                created_count += 1
        except Exception as e:
            # Index might already exist or column might not exist yet
            print(f"Note: Could not create index {index_name}: {e}")

    if created_count > 0:
        print(f"✓ Created {created_count} database indexes for performance")
