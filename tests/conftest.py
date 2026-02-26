"""Test configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import Base, get_db
from app.db.models import Invoice

# Test database URL (SQLite for testing)
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_ocr_input():
    """Sample OCR input data."""
    return {
        "raw_text": "INVOICE\\nInvoice #: INV-2024-001\\nDate: 2024-01-15",
        "extracted_fields": {
            "invoice_number": "INV-2024-001",
            "date": "2024-01-15",
            "vendor": "Acme Corporation",
            "vendor_address": "123 Business St, City, State 12345",
            "total": "1234.56",
            "currency": "USD",
        },
        "confidence_score": 95.5,
    }


@pytest.fixture
def sample_invoice_create():
    """Sample invoice create data."""
    from datetime import datetime
    from decimal import Decimal
    from app.schemas.invoice import InvoiceCreate

    return InvoiceCreate(
        invoice_number="INV-2024-001",
        invoice_date=datetime(2024, 1, 15),
        vendor_name="Acme Corporation",
        vendor_address="123 Business St, City, State 12345",
        total_amount=Decimal("1234.56"),
        currency="USD",
    )
