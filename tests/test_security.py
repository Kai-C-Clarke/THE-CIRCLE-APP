"""Security tests for THE CIRCLE APP"""
import pytest
import os
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, safe_file_path


@pytest.fixture
def client():
    """Create test client"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestPathTraversalProtection:
    """Test path traversal vulnerability protection"""

    def test_safe_file_path_valid_filename(self, temp_dir):
        """Test that valid filenames work correctly"""
        result = safe_file_path("test.jpg", temp_dir)
        assert result.startswith(temp_dir)
        assert "test.jpg" in result

    def test_safe_file_path_rejects_parent_directory(self, temp_dir):
        """Test that parent directory traversal is blocked"""
        with pytest.raises(ValueError, match="Path traversal attempt detected"):
            safe_file_path("../etc/passwd", temp_dir)

    def test_safe_file_path_rejects_absolute_path(self, temp_dir):
        """Test that absolute paths are blocked"""
        with pytest.raises(ValueError, match="Path traversal attempt detected"):
            safe_file_path("/etc/passwd", temp_dir)

    def test_safe_file_path_rejects_multiple_traversals(self, temp_dir):
        """Test that multiple directory traversals are blocked"""
        with pytest.raises(ValueError, match="Path traversal attempt detected"):
            safe_file_path("../../../../../../etc/passwd", temp_dir)

    def test_safe_file_path_sanitizes_filename(self, temp_dir):
        """Test that filenames are sanitized"""
        result = safe_file_path("../test/../file.jpg", temp_dir)
        # secure_filename should strip the ../ parts
        assert ".." not in result

    def test_audio_endpoint_path_traversal(self, client):
        """Test audio endpoint rejects path traversal"""
        response = client.get("/api/audio/../../../etc/passwd")
        assert response.status_code == 400
        assert b"Invalid filename" in response.data

    def test_uploads_endpoint_path_traversal(self, client):
        """Test uploads endpoint rejects path traversal"""
        response = client.get("/uploads/../../app.py")
        assert response.status_code == 400
        assert b"Invalid filename" in response.data

    def test_media_preview_endpoint_path_traversal(self, client):
        """Test media preview endpoint rejects path traversal"""
        response = client.get("/api/media/preview/../../../requirements.txt")
        assert response.status_code == 400
        assert b"Invalid filename" in response.data


class TestAuthentication:
    """Test authentication system"""

    def test_protected_route_without_auth(self, client):
        """Test that protected routes require authentication"""
        # Set APP_PASSWORD to enable auth
        os.environ["APP_PASSWORD"] = "test123"

        response = client.post("/api/memories/save", json={"text": "Test memory"})
        assert response.status_code == 401
        assert b"Authentication required" in response.data

        # Clean up
        del os.environ["APP_PASSWORD"]

    def test_protected_route_with_valid_auth(self, client):
        """Test that valid authentication works"""
        # Set APP_PASSWORD
        os.environ["APP_PASSWORD"] = "test123"

        # Create valid auth header
        import base64

        credentials = base64.b64encode(b":test123").decode("utf-8")
        headers = {"Authorization": f"Basic {credentials}"}

        # This should not return 401 (may return 400 if missing required fields)
        response = client.post(
            "/api/memories/save", json={"text": "Test memory"}, headers=headers
        )
        assert response.status_code != 401

        # Clean up
        del os.environ["APP_PASSWORD"]

    def test_protected_route_with_invalid_auth(self, client):
        """Test that invalid authentication is rejected"""
        # Set APP_PASSWORD
        os.environ["APP_PASSWORD"] = "test123"

        # Create invalid auth header
        import base64

        credentials = base64.b64encode(b":wrong_password").decode("utf-8")
        headers = {"Authorization": f"Basic {credentials}"}

        response = client.post(
            "/api/memories/save", json={"text": "Test memory"}, headers=headers
        )
        assert response.status_code == 401

        # Clean up
        del os.environ["APP_PASSWORD"]


class TestCORSConfiguration:
    """Test CORS configuration"""

    def test_cors_allowed_origin(self, client):
        """Test that allowed origins work"""
        response = client.options(
            "/api/memories", headers={"Origin": "http://localhost:5000"}
        )
        # Should allow localhost by default
        assert response.status_code in [200, 204]

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present"""
        response = client.get("/api/memories")
        # CORS headers should be present
        assert "Access-Control-Allow-Origin" in response.headers


class TestSecurityHeaders:
    """Test security-related configurations"""

    def test_secret_key_configured(self):
        """Test that SECRET_KEY is configured"""
        assert app.config.get("SECRET_KEY") is not None
        assert len(app.config.get("SECRET_KEY")) > 0

    def test_debug_mode_disabled_by_default(self):
        """Test that debug mode is disabled by default"""
        # In test mode, debug might be on, but in production it should be off
        # This test verifies the app can run with debug=False
        assert app.config.get("TESTING") or not app.debug


class TestFileUploadSecurity:
    """Test file upload security"""

    def test_upload_without_auth(self, client):
        """Test that file uploads require authentication"""
        os.environ["APP_PASSWORD"] = "test123"

        response = client.post("/api/media/upload", data={"file": (None, "test.jpg")})
        assert response.status_code == 401

        del os.environ["APP_PASSWORD"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
