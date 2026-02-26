# API Usage Guide

## Base URL

```
Development: http://localhost:8000
Production: https://api.your-domain.com
```

## API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

## Authentication

_Note: Current version doesn't require authentication. For production, implement JWT/OAuth._

## Endpoints

### 1. Health Check

Check if the service is running.

**Endpoint**: `GET /api/v1/health`

**Response**:

```json
{
  "status": "healthy",
  "service": "Enterprise Document Integration Service"
}
```

**cURL Example**:

```bash
curl http://localhost:8000/api/v1/health
```

---

### 2. Process OCR Document

Process raw OCR output and create an invoice.

**Endpoint**: `POST /api/v1/process-ocr`

**Request Body**:

```json
{
  "raw_text": "INVOICE\nInvoice #: INV-2024-001\nDate: 2024-01-15...",
  "extracted_fields": {
    "invoice_number": "INV-2024-001",
    "date": "2024-01-15",
    "vendor": "Acme Corporation",
    "vendor_address": "123 Business St, City, State 12345",
    "total": "1234.56",
    "currency": "USD"
  },
  "confidence_score": 95.5
}
```

**Success Response** (201 Created):

```json
{
  "success": true,
  "message": "Invoice INV-2024-001 processed successfully",
  "invoice": {
    "id": 1,
    "invoice_number": "INV-2024-001",
    "invoice_date": "2024-01-15T00:00:00",
    "due_date": null,
    "vendor_name": "Acme Corporation",
    "vendor_address": "123 Business St, City, State 12345",
    "vendor_tax_id": null,
    "customer_name": null,
    "customer_address": null,
    "subtotal": null,
    "tax_amount": null,
    "total_amount": "1234.56",
    "currency": "USD",
    "confidence_score": "95.50",
    "status": "processed",
    "error_message": null,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "processed_at": "2024-01-15T10:30:00"
  },
  "errors": null
}
```

**Error Response** (200 OK with success: false):

```json
{
  "success": false,
  "message": "Failed to map OCR data to invoice schema",
  "invoice": null,
  "errors": {
    "invoice_number": "Invoice number is required but not found in OCR data",
    "total_amount": "Total amount is required and must be positive"
  }
}
```

**cURL Example**:

```bash
curl -X POST http://localhost:8000/api/v1/process-ocr \
  -H "Content-Type: application/json" \
  -d '{
    "extracted_fields": {
      "invoice_number": "INV-2024-001",
      "date": "2024-01-15",
      "vendor": "Acme Corporation",
      "total": "1234.56"
    },
    "confidence_score": 95.5
  }'
```

**Python Example**:

```python
import requests

url = "http://localhost:8000/api/v1/process-ocr"
data = {
    "extracted_fields": {
        "invoice_number": "INV-2024-001",
        "date": "2024-01-15",
        "vendor": "Acme Corporation",
        "total": "1234.56"
    },
    "confidence_score": 95.5
}

response = requests.post(url, json=data)
result = response.json()

if result["success"]:
    print(f"Invoice created: {result['invoice']['id']}")
else:
    print(f"Error: {result['errors']}")
```

---

### 3. Get All Invoices

Retrieve a paginated list of invoices.

**Endpoint**: `GET /api/v1/invoices`

**Query Parameters**:

- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 50, max: 100)
- `status` (string, optional): Filter by status (pending, processed, failed)

**Response**:

```json
{
  "total": 150,
  "skip": 0,
  "limit": 50,
  "invoices": [
    {
      "id": 1,
      "invoice_number": "INV-2024-001",
      "invoice_date": "2024-01-15T00:00:00",
      "vendor_name": "Acme Corporation",
      "total_amount": "1234.56",
      "currency": "USD",
      "status": "processed",
      ...
    },
    ...
  ]
}
```

**cURL Examples**:

```bash
# Get first 50 invoices
curl http://localhost:8000/api/v1/invoices

# Get invoices with pagination
curl "http://localhost:8000/api/v1/invoices?skip=50&limit=25"

# Filter by status
curl "http://localhost:8000/api/v1/invoices?status=processed"

# Combine filters
curl "http://localhost:8000/api/v1/invoices?skip=0&limit=10&status=processed"
```

**Python Example**:

```python
import requests

# Get all processed invoices
url = "http://localhost:8000/api/v1/invoices"
params = {
    "skip": 0,
    "limit": 100,
    "status": "processed"
}

response = requests.get(url, params=params)
data = response.json()

print(f"Total invoices: {data['total']}")
for invoice in data['invoices']:
    print(f"  {invoice['invoice_number']}: ${invoice['total_amount']}")
```

---

### 4. Get Invoice by ID

Retrieve a specific invoice by its ID.

**Endpoint**: `GET /api/v1/invoices/{invoice_id}`

**Path Parameters**:

- `invoice_id` (int): The invoice ID

**Success Response** (200 OK):

```json
{
  "id": 1,
  "invoice_number": "INV-2024-001",
  "invoice_date": "2024-01-15T00:00:00",
  "due_date": "2024-02-15T00:00:00",
  "vendor_name": "Acme Corporation",
  "vendor_address": "123 Business St, City, State 12345",
  "vendor_tax_id": "12-3456789",
  "customer_name": "XYZ Company",
  "customer_address": "456 Client Ave, Town, State 67890",
  "subtotal": "1100.00",
  "tax_amount": "134.56",
  "total_amount": "1234.56",
  "currency": "USD",
  "confidence_score": "95.50",
  "status": "processed",
  "error_message": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "processed_at": "2024-01-15T10:30:00"
}
```

**Error Response** (404 Not Found):

```json
{
  "detail": "Invoice with id 999 not found"
}
```

**cURL Example**:

```bash
curl http://localhost:8000/api/v1/invoices/1
```

**Python Example**:

```python
import requests

invoice_id = 1
url = f"http://localhost:8000/api/v1/invoices/{invoice_id}"

response = requests.get(url)

if response.status_code == 200:
    invoice = response.json()
    print(f"Invoice: {invoice['invoice_number']}")
    print(f"Amount: {invoice['currency']} {invoice['total_amount']}")
elif response.status_code == 404:
    print("Invoice not found")
```

---

## Field Mapping Reference

The OCR mapper recognizes various field name variations:

| Invoice Field  | Recognized OCR Field Names                                  |
| -------------- | ----------------------------------------------------------- |
| invoice_number | invoice_number, invoice_no, inv_no, number, invoice#        |
| invoice_date   | invoice_date, date, inv_date, bill_date, issue_date         |
| due_date       | due_date, payment_due, due, payment_date                    |
| vendor_name    | vendor_name, vendor, supplier, from, seller, company        |
| vendor_address | vendor_address, vendor_addr, from_address, supplier_address |
| total_amount   | total_amount, total, grand_total, amount_due, balance_due   |
| currency       | currency, curr, currency_code                               |

---

## Error Codes

| Status Code | Description                                                |
| ----------- | ---------------------------------------------------------- |
| 200         | Success (but check response.success for processing errors) |
| 201         | Created successfully                                       |
| 400         | Bad request (invalid parameters)                           |
| 404         | Resource not found                                         |
| 422         | Unprocessable entity (mapping error)                       |
| 500         | Internal server error                                      |

---

## Complete Integration Example

### Python Integration

```python
import requests
from typing import Dict, Any, Optional

class OCRServiceClient:
    """Client for Enterprise Document Integration Service."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1"

    def process_ocr(self, extracted_fields: Dict[str, Any],
                    raw_text: Optional[str] = None,
                    confidence_score: Optional[float] = None) -> Dict:
        """Process OCR data and create invoice."""
        url = f"{self.base_url}{self.api_prefix}/process-ocr"
        payload = {
            "extracted_fields": extracted_fields,
            "raw_text": raw_text,
            "confidence_score": confidence_score
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_invoices(self, skip: int = 0, limit: int = 50,
                     status: Optional[str] = None) -> Dict:
        """Get list of invoices."""
        url = f"{self.base_url}{self.api_prefix}/invoices"
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_invoice(self, invoice_id: int) -> Dict:
        """Get specific invoice by ID."""
        url = f"{self.base_url}{self.api_prefix}/invoices/{invoice_id}"

        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> bool:
        """Check if service is healthy."""
        url = f"{self.base_url}{self.api_prefix}/health"

        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False


# Usage example
if __name__ == "__main__":
    client = OCRServiceClient("http://localhost:8000")

    # Check health
    if not client.health_check():
        print("Service is not available")
        exit(1)

    # Process OCR document
    ocr_data = {
        "invoice_number": "INV-2024-001",
        "date": "2024-01-15",
        "vendor": "Acme Corporation",
        "total": "1234.56"
    }

    result = client.process_ocr(ocr_data, confidence_score=95.5)

    if result["success"]:
        invoice_id = result["invoice"]["id"]
        print(f"✓ Invoice created with ID: {invoice_id}")

        # Retrieve the invoice
        invoice = client.get_invoice(invoice_id)
        print(f"✓ Invoice {invoice['invoice_number']}: ${invoice['total_amount']}")
    else:
        print(f"✗ Processing failed: {result['errors']}")

    # Get all invoices
    invoices = client.get_invoices(limit=10)
    print(f"✓ Total invoices: {invoices['total']}")
```

### JavaScript/Node.js Integration

```javascript
const axios = require("axios");

class OCRServiceClient {
  constructor(baseURL = "http://localhost:8000") {
    this.client = axios.create({
      baseURL: `${baseURL}/api/v1`,
      headers: { "Content-Type": "application/json" },
    });
  }

  async processOCR(extractedFields, rawText = null, confidenceScore = null) {
    const response = await this.client.post("/process-ocr", {
      extracted_fields: extractedFields,
      raw_text: rawText,
      confidence_score: confidenceScore,
    });
    return response.data;
  }

  async getInvoices(skip = 0, limit = 50, status = null) {
    const params = { skip, limit };
    if (status) params.status = status;

    const response = await this.client.get("/invoices", { params });
    return response.data;
  }

  async getInvoice(invoiceId) {
    const response = await this.client.get(`/invoices/${invoiceId}`);
    return response.data;
  }

  async healthCheck() {
    try {
      const response = await this.client.get("/health");
      return response.status === 200;
    } catch {
      return false;
    }
  }
}

// Usage
(async () => {
  const client = new OCRServiceClient("http://localhost:8000");

  const result = await client.processOCR(
    {
      invoice_number: "INV-2024-001",
      date: "2024-01-15",
      vendor: "Acme Corporation",
      total: "1234.56",
    },
    null,
    95.5,
  );

  if (result.success) {
    console.log(`Invoice created: ${result.invoice.id}`);
  }
})();
```

---

## Rate Limiting

_Note: Rate limiting not currently implemented. Recommended for production._

Suggested limits:

- 100 requests per minute per IP
- 1000 requests per hour per IP

---

## Best Practices

1. **Always check the `success` field** in the response for `/process-ocr`
2. **Handle pagination** when retrieving large datasets
3. **Validate data** before sending to the API
4. **Use appropriate timeouts** for HTTP requests
5. **Log all API interactions** for debugging
6. **Implement retry logic** for transient failures

---

## Support

For API questions or issues:

- Check `/docs` for interactive documentation
- Review logs for error details
- See DEPLOYMENT.md for infrastructure issues
