"""Test script for line items feature."""

import requests
import json
from datetime import datetime

# Generate unique invoice number
invoice_num = f"INV-2024-{datetime.now().strftime('%H%M%S')}"

# Test data with line items
test_data = {
    "document_id": f"doc-{datetime.now().strftime('%H%M%S')}",
    "extracted_fields": {
        "invoice_number": invoice_num,
        "invoice_date": "2024-02-15",
        "due_date": "2024-03-15",
        "vendor_name": "Tech Solutions Inc",
        "vendor_address": "789 Tech Blvd, San Francisco, CA 94107",
        "vendor_tax_id": "98-7654321",
        "customer_name": "Global Corp",
        "customer_address": "456 Business Ave, New York, NY 10001",
        "items": [
            {
                "description": "Software License - Enterprise",
                "qty": 5,
                "unit_price": 499.99,
                "amount": 2499.95,
            },
            {
                "description": "Technical Support - Premium",
                "qty": 1,
                "unit_price": 1500.00,
                "amount": 1500.00,
            },
            {
                "description": "Training Sessions",
                "qty": 3,
                "unit_price": 350.00,
                "amount": 1050.00,
            },
        ],
        "subtotal": 5049.95,
        "tax": 454.50,
        "total": 5504.45,
        "currency": "USD",
    },
    "confidence_score": 96.5,
}

print("Testing POST /api/v1/process-ocr with line items...")
print("-" * 60)

try:
    response = requests.post(
        "http://localhost:8000/api/v1/process-ocr", json=test_data, timeout=10
    )

    print(f"Status Code: {response.status_code}")
    print("\nResponse:")
    print(json.dumps(response.json(), indent=2))

    if response.status_code in [200, 201]:
        invoice_data = response.json()
        if invoice_data.get("success"):
            invoice = invoice_data.get("invoice", {})
            invoice_id = invoice.get("id")

            print("\n" + "=" * 60)
            print(f"✓ Invoice created successfully with ID: {invoice_id}")

            # Test GET to retrieve the invoice with line items
            print("\n" + "=" * 60)
            print(f"Testing GET /api/v1/invoices/{invoice_id}...")
            print("-" * 60)

            get_response = requests.get(
                f"http://localhost:8000/api/v1/invoices/{invoice_id}", timeout=10
            )

            print(f"Status Code: {get_response.status_code}")
            print("\nResponse:")
            retrieved = get_response.json()
            print(json.dumps(retrieved, indent=2))

            # Check if line items are included
            items = retrieved.get("items")
            if items:
                print("\n" + "=" * 60)
                print(f"✓ Line items retrieved successfully ({len(items)} items):")
                for i, item in enumerate(items, 1):
                    print(f"\n  Item {i}:")
                    print(f"    Description: {item['description']}")
                    print(
                        f"    Quantity: {item.get('qty', item.get('quantity', 'N/A'))}"
                    )
                    print(f"    Unit Price: ${item['unit_price']}")
                    print(f"    Amount: ${item['amount']}")
            else:
                print("\n✗ No line items found in response")
        else:
            print(f"\n✗ Failed: {invoice_data.get('message')}")
            print(f"Errors: {invoice_data.get('errors')}")
    else:
        print(f"\n✗ Request failed with status {response.status_code}")

except requests.exceptions.ConnectionError:
    print(
        "✗ Could not connect to server. Make sure it's running on http://localhost:8000"
    )
except Exception as e:
    print(f"✗ Error: {e}")
