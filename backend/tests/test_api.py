"""Tests for FastAPI API endpoints."""

from fastapi.testclient import TestClient

from daily_scheduler.main import app

client = TestClient(app)


class TestDashboardEndpoint:
    def test_dashboard_endpoint_exists(self):
        routes = [r.path for r in app.routes]
        assert "/api/dashboard" in routes


class TestSettingsEndpoint:
    def test_get_settings(self):
        response = client.get("/api/settings")
        assert response.status_code == 200
        data = response.json()
        assert "smtp_host" in data
        assert "report_language" in data

    def test_health_check(self):
        response = client.get("/api/settings/status")
        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert "claude_cli" in data
        assert "smtp_configured" in data


class TestPipelineEndpoint:
    def test_get_pipeline_status(self):
        response = client.get("/api/pipeline/status")
        assert response.status_code == 200
        data = response.json()
        assert "running" in data
