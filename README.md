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

# Quick setup with helper script
chmod +x dev.sh
./dev.sh setup        # Set up virtual environment
./dev.sh db-init      # Initialize database
./dev.sh run          # Start development server

# Or manual setup:
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Initialize database
python -c "from app.db.session import init_db; init_db()"

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
│   ├── api/
│   │   └── routes.py        # API route handlers
│   ├── core/
│   │   ├── config.py        # Configuration management
│   │   ├── logging.py       # Structured logging setup
│   │   └── exceptions.py    # Custom exceptions
│   ├── db/
│   │   ├── session.py       # Database session management
│   │   ├── models.py        # SQLAlchemy models
│   │   └── crud.py          # Database operations
│   ├── schemas/
│   │   └── invoice.py       # Pydantic schemas
│   └── services/
│       ├── mapper.py        # OCR to invoice mapping
│       └── validator.py     # Business rule validation
├── tests/                   # Test suite
│   ├── conftest.py         # Test fixtures
│   ├── test_mapper.py      # Mapper tests
│   ├── test_validator.py   # Validator tests
│   └── test_api.py         # API endpoint tests
├── requirements.txt         # Python dependencies
├── Dockerfile
├── docker-compose.yml
├── dev.sh                   # Development helper script
├── .env.example            # Environment variables template
├── README.md
├── API_GUIDE.md            # API documentation
└── DEPLOYMENT.md           # Deployment guide
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
