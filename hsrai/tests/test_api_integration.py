"""Integration tests for the HSRAI API server."""

import os

import pytest

os.environ["HSRAI_API_KEY"] = "test-key-123"
os.environ["HSRAI_KEY_PATH"] = ""

from starlette.testclient import TestClient

from hsrai.api.server import app

HEADERS = {"X-API-Key": "test-key-123"}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"
        assert "uptime_seconds" in data
        assert "certificates_issued" in data
        assert "requests_total" in data

    def test_health_no_auth_required(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200


class TestProcessEndpoint:
    def test_process_basic(self, client):
        resp = client.post("/process", json={"text": "hello world"}, headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "content" in data
        assert "format" in data
        assert "processing_time_ms" in data
        assert data["processing_time_ms"] >= 0

    def test_process_returns_trust_certificate(self, client):
        resp = client.post("/process", json={"text": "test query"}, headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("trust_certificate_id") is not None

    def test_process_empty_text_rejected(self, client):
        resp = client.post("/process", json={"text": ""}, headers=HEADERS)
        assert resp.status_code == 422

    def test_process_no_api_key_rejected(self, client):
        resp = client.post("/process", json={"text": "test"})
        assert resp.status_code == 401

    def test_process_wrong_api_key_rejected(self, client):
        resp = client.post(
            "/process", json={"text": "test"}, headers={"X-API-Key": "wrong-key"}
        )
        assert resp.status_code == 401


class TestVerifyEndpoint:
    def test_verify_nonexistent_cert(self, client):
        resp = client.post(
            "/verify", json={"certificate_id": "nonexistent"}, headers=HEADERS
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is False
        assert "not found" in data["message"]

    def test_verify_after_process(self, client):
        proc_resp = client.post(
            "/process", json={"text": "verify me"}, headers=HEADERS
        )
        cert_id = proc_resp.json().get("trust_certificate_id")
        assert cert_id is not None

        verify_resp = client.post(
            "/verify", json={"certificate_id": cert_id}, headers=HEADERS
        )
        assert verify_resp.status_code == 200
        assert verify_resp.json()["valid"] is True

    def test_verify_no_auth_rejected(self, client):
        resp = client.post("/verify", json={"certificate_id": "test"})
        assert resp.status_code == 401


class TestMetricsEndpoint:
    def test_metrics_prometheus_format(self, client):
        client.post("/process", json={"text": "metrics test"}, headers=HEADERS)
        resp = client.get("/metrics")
        assert resp.status_code == 200
        text = resp.text
        assert "hsrai_requests_total" in text
        assert "hsrai_errors_total" in text

    def test_metrics_json_format(self, client):
        resp = client.get("/metrics/json")
        assert resp.status_code == 200
        data = resp.json()
        assert "requests_total" in data
        assert "avg_processing_time" in data


class TestQueueStatusEndpoint:
    def test_queue_status(self, client):
        resp = client.get("/queue/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "active_requests" in data
        assert "max_concurrent" in data
        assert "available_slots" in data
