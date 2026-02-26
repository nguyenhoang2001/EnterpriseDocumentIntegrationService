# Enterprise Document Integration Service

A production-ready backend service for processing OCR output and integrating document data into business systems.

## Overview

This service provides a robust pipeline for:
- Receiving raw OCR output (JSON format)
- Mapping OCR data into structured business schemas (invoices)
- Validating required fields and data types
- Persisting data to SQL database
- Exposing RESTful APIs for data retrieval
- Comprehensive logging and error handling

## Features

- ✅ RESTful API built with FastAPI
- ✅ Clean architecture with separation of concerns
- ✅ Pydantic-based data validation
- ✅ SQLAlchemy ORM for database operations
- ✅ Structured logging for observability
- ✅ Comprehensive error handling
- ✅ Docker support for easy deployment
- ✅ AWS-ready architecture

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Validation:** Pydantic
- **Testing:** pytest
- **Containerization:** Docker
- **Deployment:** AWS-ready

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL
- Docker (optional)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ocr

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
python -m app.database

# Start the service
uvicorn app.main:app --reload
```

### Using Docker

```bash
# Build and run with docker-compose
docker-compose up --build

# The API will be available at http://localhost:8000
```

## API Endpoints

### Process OCR Document
```
POST /api/v1/process-ocr
Content-Type: application/json

{
  "raw_text": "Invoice #12345...",
  "extracted_fields": {
    "invoice_number": "12345",
    "date": "2024-01-15",
    "vendor": "Acme Corp",
    "total_amount": "1234.56"
  }
}
```

### Get All Invoices
```
GET /api/v1/invoices?skip=0&limit=100
```

### Get Invoice by ID
```
GET /api/v1/invoices/{invoice_id}
```

## Project Structure

```
ocr/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup and session management
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── api/                 # API routes
│   └── utils/               # Utilities (logging, exceptions)
├── tests/                   # Test suite
├── docker/                  # Docker configuration
├── requirements.txt         # Python dependencies
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Development

### Running Tests
```bash
pytest
pytest --cov=app tests/
```

### Code Quality
```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed AWS deployment instructions.

## License

MIT License

## Author

Built as a demonstration of enterprise-grade Python backend development.
