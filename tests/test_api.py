"""Tests for API endpoints."""

import pytest
from datetime import datetime


class TestAPIEndpoints:
    """Test cases for API endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data

    def test_process_ocr_success(self, client, sample_ocr_input):
        """Test successful OCR processing."""
        response = client.post("/api/v1/process-ocr", json=sample_ocr_input)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["invoice"] is not None
        assert data["invoice"]["invoice_number"] == "INV-2024-001"

    def test_process_ocr_missing_fields(self, client):
        """Test OCR processing with missing required fields."""
        incomplete_input = {
            "extracted_fields": {
                "date": "2024-01-15"
                # Missing invoice_number, vendor, and total
            }
        }

        response = client.post("/api/v1/process-ocr", json=incomplete_input)

        data = response.json()
        assert data["success"] is False
        assert data["errors"] is not None

    def test_get_invoices(self, client, sample_ocr_input):
        """Test getting list of invoices."""
        # First create an invoice
        client.post("/api/v1/process-ocr", json=sample_ocr_input)

        # Then retrieve the list
        response = client.get("/api/v1/invoices")

        assert response.status_code == 200
        data = response.json()
        assert "invoices" in data
        assert "total" in data
        assert data["total"] >= 1
        assert len(data["invoices"]) >= 1

    def test_get_invoices_pagination(self, client, sample_ocr_input):
        """Test invoice list pagination."""
        # Create multiple invoices
        for i in range(3):
            ocr_data = sample_ocr_input.copy()
            ocr_data["extracted_fields"]["invoice_number"] = f"INV-{i:03d}"
            client.post("/api/v1/process-ocr", json=ocr_data)

        # Test pagination
        response = client.get("/api/v1/invoices?skip=0&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["invoices"]) == 2
        assert data["total"] >= 3

    def test_get_invoice_by_id(self, client, sample_ocr_input):
        """Test getting a specific invoice by ID."""
        # Create an invoice
        create_response = client.post("/api/v1/process-ocr", json=sample_ocr_input)
        invoice_id = create_response.json()["invoice"]["id"]

        # Retrieve it
        response = client.get(f"/api/v1/invoices/{invoice_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == invoice_id
        assert data["invoice_number"] == "INV-2024-001"

    def test_get_invoice_not_found(self, client):
        """Test getting non-existent invoice returns 404."""
        response = client.get("/api/v1/invoices/99999")

        assert response.status_code == 404

    def test_get_invoices_with_status_filter(self, client, sample_ocr_input):
        """Test filtering invoices by status."""
        # Create an invoice
        client.post("/api/v1/process-ocr", json=sample_ocr_input)

        # Filter by status
        response = client.get("/api/v1/invoices?status=processed")

        assert response.status_code == 200
        data = response.json()
        assert all(inv["status"] == "processed" for inv in data["invoices"])
