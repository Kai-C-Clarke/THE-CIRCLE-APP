#!/usr/bin/env python3
"""
create_admin.py - Interactive script to create admin users

Usage:
    python create_admin.py              # Interactive mode
    python create_admin.py --quick      # Quick mode with auto-generated password
"""

import sys
import getpass
import secrets
from auth import create_user
from database import init_db, migrate_db


def create_admin_interactive():
    """Create admin user with interactive prompts."""
    print("=" * 60)
    print("CREATE ADMIN USER")
    print("=" * 60)

    username = input("Username (min 3 chars): ").strip()
    if not username:
        print("❌ Username cannot be empty")
        return False

    email = input("Email: ").strip()
    if not email:
        print("❌ Email cannot be empty")
        return False

    password = getpass.getpass("Password (min 8 chars): ")
    if not password:
        print("❌ Password cannot be empty")
        return False

    password_confirm = getpass.getpass("Confirm password: ")

    if password != password_confirm:
        print("❌ Passwords do not match")
        return False

    # Create the user
    success, result = create_user(username, email, password, is_admin=True)

    if success:
        print("=" * 60)
        print(f"✅ Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   User ID: {result}")
        print("=" * 60)
        return True
    else:
        print(f"❌ Error creating user: {result}")
        return False


def create_admin_quick():
    """Create admin user with auto-generated password."""
    username = f"admin_{secrets.token_hex(4)}"
    email = f"{username}@localhost"
    password = secrets.token_urlsafe(16)

    print("=" * 60)
    print("QUICK ADMIN USER CREATION")
    print("=" * 60)

    success, result = create_user(username, email, password, is_admin=True)

    if success:
        print(f"✅ Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   User ID: {result}")
        print()
        print("⚠️  IMPORTANT: Save these credentials!")
        print("=" * 60)
        return True
    else:
        print(f"❌ Error creating user: {result}")
        print("=" * 60)
        return False


def main():
    """Main entry point."""
    # Initialize database
    init_db()
    migrate_db()

    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = create_admin_quick()
    else:
        success = create_admin_interactive()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
