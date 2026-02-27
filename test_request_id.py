"""Test script to verify request_id in structured logs using FastAPI TestClient."""

import json
from fastapi.testclient import TestClient
from app.main import app
from app.core.logging import get_error_counts

# Use FastAPI TestClient - no external server needed
client = TestClient(app, raise_server_exceptions=False)

# Sample OCR data
test_data = {
    "document_id": "test-doc-123",
    "extracted_fields": {
        "invoice_number": "INV-2024-001",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "vendor_name": "ABC Company",
        "vendor_address": "123 Main St, City",
        "customer_name": "XYZ Corp",
        "total_amount": "1500.00",
        "subtotal": "1250.00",
        "tax_amount": "250.00",
        "currency": "USD",
    },
    "confidence_score": 95.5,
    "processing_time": 1.25,
}


def test_root_endpoint():
    """Test root endpoint."""
    print("Testing root endpoint...")
    response = client.get("/")

    print(f"Status: {response.status_code}")
    print(f"Request-ID: {response.headers.get('X-Request-ID')}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("\n" + "=" * 50 + "\n")


def test_with_custom_request_id():
    """Test with a custom X-Request-ID header."""
    headers = {
        "Content-Type": "application/json",
        "X-Request-ID": "custom-request-id-12345",
    }

    print("Testing with custom Request-ID...")
    response = client.post("/api/v1/process-ocr", json=test_data, headers=headers)

    print(f"Status: {response.status_code}")
    print(f"Response Request-ID: {response.headers.get('X-Request-ID')}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("\n" + "=" * 50 + "\n")


def test_without_request_id():
    """Test without request ID (should auto-generate a UUID)."""
    print("Testing without Request-ID (auto-generate)...")
    response = client.post("/api/v1/process-ocr", json=test_data)

    print(f"Status: {response.status_code}")
    print(f"Generated Request-ID: {response.headers.get('X-Request-ID')}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("\n" + "=" * 50 + "\n")


def test_error_counts():
    """Show accumulated error counts after all requests."""
    counts = get_error_counts()
    print("Error counts accumulated during this test run:")
    if counts:
        print(json.dumps(counts, indent=2))
    else:
        print("  (no errors logged yet)")
    print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    print("Request ID Logging Test")
    print("=" * 50 + "\n")

    test_root_endpoint()
    test_with_custom_request_id()
    test_without_request_id()
    test_error_counts()

    print("✅ All tests completed!")
    print("Check the JSON log output above for 'request_id' and 'error_counts' fields.")
