"""Tests for invoice validator service."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from app.services.validator import InvoiceValidator
from app.schemas.invoice import InvoiceCreate
from app.core.exceptions import ValidationError


class TestInvoiceValidator:
    """Test cases for invoice validator."""

    def test_valid_invoice(self, sample_invoice_create):
        """Test validation passes for valid invoice."""
        validator = InvoiceValidator()

        result = validator.validate_invoice(sample_invoice_create)

        assert result["valid"] is True
        assert isinstance(result["warnings"], list)

    def test_invalid_invoice_number(self):
        """Test validation fails for invalid invoice number."""
        validator = InvoiceValidator()

        invoice = InvoiceCreate(
            invoice_number="  ",  # Invalid: whitespace only
            invoice_date=datetime.now(),
            vendor_name="Acme Corp",
            total_amount=Decimal("100.00"),
        )

        with pytest.raises(ValidationError):
            validator.validate_invoice(invoice)

    def test_negative_total_amount(self):
        """Test validation fails for negative total amount."""
        validator = InvoiceValidator()

        with pytest.raises(ValidationError):
            invoice = InvoiceCreate(
                invoice_number="INV-001",
                invoice_date=datetime.now(),
                vendor_name="Acme Corp",
                total_amount=Decimal("-100.00"),  # Negative amount
            )
            validator.validate_invoice(invoice)

    def test_due_date_before_invoice_date(self):
        """Test validation fails when due date is before invoice date."""
        validator = InvoiceValidator()

        invoice_date = datetime.now()
        due_date = invoice_date - timedelta(days=1)

        invoice = InvoiceCreate(
            invoice_number="INV-001",
            invoice_date=invoice_date,
            due_date=due_date,
            vendor_name="Acme Corp",
            total_amount=Decimal("100.00"),
        )

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_invoice(invoice)

        assert "due_date" in str(exc_info.value.details)

    def test_invalid_currency(self):
        """Test validation fails for unsupported currency."""
        validator = InvoiceValidator()

        invoice = InvoiceCreate(
            invoice_number="INV-001",
            invoice_date=datetime.now(),
            vendor_name="Acme Corp",
            total_amount=Decimal("100.00"),
            currency="XYZ",  # Invalid currency
        )

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_invoice(invoice)

        assert "Currency" in str(exc_info.value.details)

    def test_amount_consistency_warning(self):
        """Test warning when subtotal + tax doesn't match total."""
        validator = InvoiceValidator()

        invoice = InvoiceCreate(
            invoice_number="INV-001",
            invoice_date=datetime.now(),
            vendor_name="Acme Corp",
            subtotal=Decimal("100.00"),
            tax_amount=Decimal("10.00"),
            total_amount=Decimal("120.00"),  # Should be 110.00
        )

        result = validator.validate_invoice(invoice)

        assert result["valid"] is True
        assert len(result["warnings"]) > 0
        assert any("match" in warning.lower() for warning in result["warnings"])

    def test_low_confidence_score_warning(self):
        """Test warning for low OCR confidence score."""
        validator = InvoiceValidator()

        invoice = InvoiceCreate(
            invoice_number="INV-001",
            invoice_date=datetime.now(),
            vendor_name="Acme Corp",
            total_amount=Decimal("100.00"),
            confidence_score=Decimal("65.0"),  # Below threshold
        )

        result = validator.validate_invoice(invoice)

        assert result["valid"] is True
        assert len(result["warnings"]) > 0
        assert any("confidence" in warning.lower() for warning in result["warnings"])
