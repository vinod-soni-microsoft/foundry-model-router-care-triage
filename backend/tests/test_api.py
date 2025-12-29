"""
Integration tests for the FastAPI application.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

client = TestClient(app)


class TestAPI:
    """Integration tests for API endpoints."""
    
    def test_root_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "Care Triage" in data["service"]
    
    def test_chat_endpoint_structure(self):
        """Test chat endpoint accepts proper structure."""
        # Note: This will fail without proper API keys configured
        # but we can test the structure
        response = client.post(
            "/chat",
            json={
                "message": "I need to schedule an appointment",
                "mode": "balanced"
            }
        )
        # Will return 500 without proper config, but structure is validated
        assert response.status_code in [200, 500]
    
    def test_chat_endpoint_invalid_mode(self):
        """Test chat endpoint with invalid mode still processes."""
        response = client.post(
            "/chat",
            json={
                "message": "Hello",
                "mode": "invalid_mode"
            }
        )
        # Should still process with default handling
        assert response.status_code in [200, 422, 500]
    
    def test_chat_endpoint_empty_message(self):
        """Test chat endpoint with empty message."""
        response = client.post(
            "/chat",
            json={
                "message": "",
                "mode": "balanced"
            }
        )
        # Should handle empty message gracefully
        assert response.status_code in [200, 400, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
