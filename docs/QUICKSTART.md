# Quick Start Guide

Get the Enterprise Document Integration Service running in under 5 minutes!

## Prerequisites

- Python 3.9+ or Docker
- PostgreSQL (or use Docker Compose)

## Option 1: Quick Start with Docker (Recommended)

```bash
# Start everything with one command
docker-compose up

# That's it! The service is now running at http://localhost:8000
```

Visit http://localhost:8000/docs to see the interactive API documentation.

## Option 2: Local Development Setup

### 1. Setup

```bash
# Clone and navigate to project
cd ocr

# Run setup script (installs dependencies)
chmod +x dev.sh
./dev.sh setup
```

### 2. Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env if needed (default settings work for local development)
```

### 3. Initialize Database

```bash
# Create database tables
./dev.sh db-init
```

### 4. Start the Service

```bash
# Run development server with hot reload
./dev.sh run
```

The API is now available at http://localhost:8000

## Test the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Process an invoice
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

# Get all invoices
curl http://localhost:8000/api/v1/invoices
```

### Using Python

```python
import requests

# Process OCR document
response = requests.post(
    "http://localhost:8000/api/v1/process-ocr",
    json={
        "extracted_fields": {
            "invoice_number": "INV-2024-001",
            "date": "2024-01-15",
            "vendor": "Acme Corporation",
            "total": "1234.56"
        },
        "confidence_score": 95.5
    }
)

result = response.json()
print(f"Success: {result['success']}")
print(f"Invoice ID: {result['invoice']['id']}")
```

### Using the Interactive Docs

1. Open http://localhost:8000/docs
2. Click on "POST /api/v1/process-ocr"
3. Click "Try it out"
4. Use this example data:

```json
{
  "extracted_fields": {
    "invoice_number": "INV-2024-001",
    "date": "2024-01-15",
    "vendor": "Acme Corporation",
    "vendor_address": "123 Business St",
    "total": "1234.56",
    "currency": "USD"
  },
  "confidence_score": 95.5
}
```

5. Click "Execute"

## Available Commands

The `dev.sh` script provides helpful shortcuts:

```bash
./dev.sh setup         # Set up environment
./dev.sh db-init       # Initialize database
./dev.sh run           # Run development server
./dev.sh test          # Run tests
./dev.sh format        # Format code
./dev.sh lint          # Lint code
./dev.sh docker-up     # Start with Docker
./dev.sh docker-down   # Stop Docker containers
./dev.sh docker-logs   # View logs
```

## Project Structure

```
app/
  ├── main.py           # Application entry point
  ├── api/routes.py     # API endpoints
  ├── core/             # Config, logging, exceptions
  ├── db/               # Database models and operations
  ├── schemas/          # Request/response models
  └── services/         # Business logic (mapper, validator)
```

## Next Steps

1. **Read the API Guide**: Check `API_GUIDE.md` for detailed endpoint documentation
2. **Explore the Code**: Start with `app/main.py` and follow the structure
3. **Run Tests**: Execute `./dev.sh test` to see the test suite
4. **Deploy**: See `DEPLOYMENT.md` for AWS deployment instructions

## Common Issues

### Port 8000 already in use

```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --port 8001
```

### Database connection error

```bash
# If using Docker, make sure PostgreSQL is running
docker-compose ps

# If running locally, check PostgreSQL is installed and running
psql --version
```

### Import errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Development Workflow

1. Make changes to code
2. Tests run automatically (if using `./dev.sh run`)
3. Check logs for any errors
4. Test endpoints using `/docs` or cURL
5. Run test suite: `./dev.sh test`
6. Format code: `./dev.sh format`
7. Commit changes with descriptive message

## Support

- **API Documentation**: http://localhost:8000/docs
- **Project README**: `README.md`
- **API Guide**: `API_GUIDE.md`
- **Deployment Guide**: `DEPLOYMENT.md`
- **Project Summary**: `PROJECT_SUMMARY.md`

## Example Workflow

```bash
# 1. Start the service
./dev.sh docker-up

# 2. Process an invoice
curl -X POST http://localhost:8000/api/v1/process-ocr \
  -H "Content-Type: application/json" \
  -d '{"extracted_fields": {"invoice_number": "INV-001", "date": "2024-01-15", "vendor": "Acme Corp", "total": "100.00"}}'

# 3. Get the invoice list
curl http://localhost:8000/api/v1/invoices

# 4. Get specific invoice
curl http://localhost:8000/api/v1/invoices/1

# 5. View logs
./dev.sh docker-logs

# 6. Stop when done
./dev.sh docker-down
```

That's it! You're ready to start developing! 🚀
