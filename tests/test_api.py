"""
Tests for the FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.api import app


@pytest.fixture
def client():
    return TestClient(app)


class TestAPI:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["version"] == "0.1.0"

    def test_market_size(self, client):
        response = client.get("/api/market-size")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_regional_benchmark(self, client):
        response = client.get("/api/regional-benchmark")
        assert response.status_code == 200

    def test_growth_leaders_default(self, client):
        response = client.get("/api/growth-leaders")
        assert response.status_code == 200
        assert len(response.json()) == 5

    def test_growth_leaders_custom_n(self, client):
        response = client.get("/api/growth-leaders?top_n=3")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_sustainability(self, client):
        response = client.get("/api/sustainability")
        assert response.status_code == 200

    def test_competitive_valid(self, client):
        response = client.get("/api/competitive/Renewables")
        assert response.status_code == 200

    def test_competitive_invalid(self, client):
        response = client.get("/api/competitive/FakeSector")
        assert response.status_code == 404

    def test_company_details(self, client):
        response = client.get("/api/company/SolarWave")
        assert response.status_code == 200
        assert response.json()["company"] == "SolarWave"

    def test_company_not_found(self, client):
        response = client.get("/api/company/FakeCompany")
        assert response.status_code == 404

    def test_compare_sectors(self, client):
        response = client.get("/api/compare?sector_a=Renewables&sector_b=Oil%20%26%20Gas")
        assert response.status_code == 200
        data = response.json()
        assert "Renewables" in data
        assert "Oil & Gas" in data
