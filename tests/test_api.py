"""API endpoint tests for THE CIRCLE APP"""
import pytest
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config["TESTING"] = True
    # Disable authentication for read-only tests
    if "APP_PASSWORD" in os.environ:
        del os.environ["APP_PASSWORD"]

    with app.test_client() as client:
        yield client


class TestReadOnlyEndpoints:
    """Test read-only API endpoints (no auth required)"""

    def test_get_memories(self, client):
        """Test GET /api/memories"""
        response = client.get("/api/memories")
        assert response.status_code == 200
        assert response.content_type == "application/json"

    def test_get_media(self, client):
        """Test GET /api/media"""
        response = client.get("/api/media")
        assert response.status_code == 200
        assert response.content_type == "application/json"

    def test_get_profile(self, client):
        """Test GET /api/profile"""
        response = client.get("/api/profile")
        assert response.status_code == 200
        assert response.content_type == "application/json"

    def test_get_categories(self, client):
        """Test GET /api/categories"""
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_index_page(self, client):
        """Test that index page loads"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data


class TestErrorHandling:
    """Test error handling"""

    def test_nonexistent_memory(self, client):
        """Test getting a non-existent memory"""
        response = client.get("/api/memories/999999")
        # Should return 404 or empty result
        assert response.status_code in [200, 404]

    def test_nonexistent_media(self, client):
        """Test getting non-existent media"""
        response = client.get("/api/media/999999")
        # Should return 404 or empty result
        assert response.status_code in [200, 404]

    def test_invalid_audio_file(self, client):
        """Test requesting non-existent audio file"""
        response = client.get("/api/audio/nonexistent.webm")
        assert response.status_code in [400, 404]


class TestJSONResponses:
    """Test that API returns valid JSON"""

    def test_memories_returns_json(self, client):
        """Test that memories endpoint returns valid JSON"""
        response = client.get("/api/memories")
        assert response.content_type == "application/json"
        data = json.loads(response.data)
        assert isinstance(data, (list, dict))

    def test_media_returns_json(self, client):
        """Test that media endpoint returns valid JSON"""
        response = client.get("/api/media")
        assert response.content_type == "application/json"
        data = json.loads(response.data)
        assert isinstance(data, (list, dict))


class TestContentTypes:
    """Test content type handling"""

    def test_json_content_type_accepted(self, client):
        """Test that JSON content type is accepted"""
        response = client.get(
            "/api/memories", headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200


class TestCORS:
    """Test CORS functionality"""

    def test_cors_preflight(self, client):
        """Test CORS preflight request"""
        response = client.options(
            "/api/memories",
            headers={
                "Origin": "http://localhost:5000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code in [200, 204]

    def test_cors_headers_on_get(self, client):
        """Test CORS headers on GET request"""
        response = client.get("/api/memories")
        # CORS headers should be present
        assert "Access-Control-Allow-Origin" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
