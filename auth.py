# auth.py - Authentication and authorization module
import os
import secrets
from functools import wraps
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, jsonify, session, g
from database import get_db

# Simple logger (THE-CIRCLE-APP doesn't have logger_config yet)
import logging
logger = logging.getLogger(__name__)


# ============================================
# USER MANAGEMENT
# ============================================

class User:
    """User model class."""

    def __init__(self, user_id, username, email, is_active=True, is_admin=False, created_at=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.is_active = is_active
        self.is_admin = is_admin
        self.created_at = created_at

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at
        }


def create_user(username, email, password, is_admin=False):
    """
    Create a new user account.

    Args:
        username: Unique username
        email: User email address
        password: Plain text password (will be hashed)
        is_admin: Whether user has admin privileges

    Returns:
        tuple: (success, user_id or error_message)
    """
    try:
        # Validate input
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters"

        if not email or '@' not in email:
            return False, "Invalid email address"

        if not password or len(password) < 8:
            return False, "Password must be at least 8 characters"

        # Check if username or email already exists
        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            return False, "Username or email already exists"

        # Hash password
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        # Create user
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, is_admin, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, is_admin, True, datetime.now().isoformat()))

        db.commit()
        user_id = cursor.lastrowid

        logger.info(f"User created: {username} (ID: {user_id}, Admin: {is_admin})")

        return True, user_id

    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        return False, "Failed to create user"


def get_user_by_id(user_id):
    """Get user by ID."""
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute('''
            SELECT id, username, email, is_active, is_admin, created_at
            FROM users
            WHERE id = ?
        ''', (user_id,))

        row = cursor.fetchone()
        if row:
            return User(
                user_id=row[0],
                username=row[1],
                email=row[2],
                is_active=row[3],
                is_admin=row[4],
                created_at=row[5]
            )

        return None

    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None


def get_user_by_username(username):
    """Get user by username."""
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute('''
            SELECT id, username, email, is_active, is_admin, created_at
            FROM users
            WHERE username = ?
        ''', (username,))

        row = cursor.fetchone()
        if row:
            return User(
                user_id=row[0],
                username=row[1],
                email=row[2],
                is_active=row[3],
                is_admin=row[4],
                created_at=row[5]
            )

        return None

    except Exception as e:
        logger.error(f"Error getting user by username: {e}")
        return None


def verify_password(username, password):
    """
    Verify user credentials.

    Args:
        username: Username
        password: Plain text password

    Returns:
        User object if valid, None if invalid
    """
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute('''
            SELECT id, username, email, password_hash, is_active, is_admin, created_at
            FROM users
            WHERE username = ?
        ''', (username,))

        row = cursor.fetchone()
        if not row:
            logger.warning(f"Login failed: User not found: {username}")
            return None

        user_id, username, email, password_hash, is_active, is_admin, created_at = row

        # Check if user is active
        if not is_active:
            logger.warning(f"Login failed: Inactive account: {username}")
            return None

        # Verify password
        if check_password_hash(password_hash, password):
            logger.info(f"Login successful: {username}")

            # Update last login
            cursor.execute('''
                UPDATE users
                SET last_login = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), user_id))
            db.commit()

            return User(user_id, username, email, is_active, is_admin, created_at)
        else:
            logger.warning(f"Login failed: Invalid password for: {username}")
            return None

    except Exception as e:
        logger.error(f"Error verifying password: {e}", exc_info=True)
        return None


def change_password(user_id, old_password, new_password):
    """
    Change user password.

    Args:
        user_id: User ID
        old_password: Current password
        new_password: New password

    Returns:
        tuple: (success, message)
    """
    try:
        # Get user
        user = get_user_by_id(user_id)
        if not user:
            return False, "User not found"

        # Verify old password
        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()

        if not row or not check_password_hash(row[0], old_password):
            return False, "Current password is incorrect"

        # Validate new password
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters"

        # Update password
        new_password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')

        cursor.execute('''
            UPDATE users
            SET password_hash = ?, updated_at = ?
            WHERE id = ?
        ''', (new_password_hash, datetime.now().isoformat(), user_id))

        db.commit()

        logger.info(f"Password changed for user: {user.username}")

        return True, "Password changed successfully"

    except Exception as e:
        logger.error(f"Error changing password: {e}", exc_info=True)
        return False, "Failed to change password"


# ============================================
# SESSION MANAGEMENT
# ============================================

def login_user(user):
    """Log in a user by setting session."""
    session.clear()
    session['user_id'] = user.id
    session['username'] = user.username
    session['is_admin'] = user.is_admin
    session.permanent = True

    logger.info(f"User logged in: {user.username} (ID: {user.id})")


def logout_user():
    """Log out the current user."""
    username = session.get('username', 'unknown')

    session.clear()
    logger.info(f"User logged out: {username}")


def get_current_user():
    """Get the current logged-in user."""
    user_id = session.get('user_id')
    if user_id:
        return get_user_by_id(user_id)
    return None


# ============================================
# DECORATORS
# ============================================

def login_required(f):
    """
    Decorator to require authentication for a route.

    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            return "This is protected"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return jsonify({'error': 'Authentication required'}), 401

        # Load user into g for access in route
        g.current_user = get_current_user()
        if not g.current_user or not g.current_user.is_active:
            session.clear()
            return jsonify({'error': 'User account not active'}), 401

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorator to require admin privileges for a route.

    Usage:
        @app.route('/admin')
        @admin_required
        def admin_route():
            return "Admin only"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        # Load user
        g.current_user = get_current_user()
        if not g.current_user or not g.current_user.is_active:
            session.clear()
            return jsonify({'error': 'User account not active'}), 401

        if not g.current_user.is_admin:
            logger.warning(f"Non-admin user {g.current_user.username} attempted to access {request.path}")
            return jsonify({'error': 'Admin privileges required'}), 403

        return f(*args, **kwargs)

    return decorated_function


# ============================================
# UTILITY FUNCTIONS
# ============================================

def count_users():
    """Get total number of users."""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        return cursor.fetchone()[0]
    except:
        return 0


def has_users():
    """Check if any users exist in the database."""
    return count_users() > 0


def generate_reset_token():
    """Generate a secure password reset token."""
    return secrets.token_urlsafe(32)


def create_initial_admin():
    """
    Create initial admin user for first-time setup.

    Returns:
        tuple: (success, credentials_dict or error_message)
    """
    try:
        # Check if users already exist
        if has_users():
            return False, "Users already exist. Use normal registration."

        # Generate random password
        temp_password = secrets.token_urlsafe(16)

        # Create admin user
        success, result = create_user(
            username='admin',
            email='admin@localhost',
            password=temp_password,
            is_admin=True
        )

        if success:
            credentials = {
                'username': 'admin',
                'password': temp_password,
                'email': 'admin@localhost'
            }

            print("=" * 60)
            print("INITIAL ADMIN ACCOUNT CREATED")
            print("=" * 60)
            print(f"Username: admin")
            print(f"Password: {temp_password}")
            print("PLEASE CHANGE THIS PASSWORD IMMEDIATELY!")
            print("=" * 60)

            return True, credentials
        else:
            return False, result

    except Exception as e:
        logger.error(f"Error creating initial admin: {e}", exc_info=True)
        return False, str(e)
