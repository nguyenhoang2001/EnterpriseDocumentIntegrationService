"""Tests for OCR mapper service."""

import pytest
from datetime import datetime
from decimal import Decimal

from app.services.mapper import OCRMapper
from app.schemas.invoice import OCRInput
from app.core.exceptions import MappingError


class TestOCRMapper:
    """Test cases for OCR mapper."""

    def test_successful_mapping(self, sample_ocr_input):
        """Test successful mapping of OCR data to invoice."""
        mapper = OCRMapper()
        ocr_input = OCRInput(**sample_ocr_input)

        result = mapper.map_ocr_to_invoice(ocr_input)

        assert result.invoice_number == "INV-2024-001"
        assert result.vendor_name == "Acme Corporation"
        assert result.total_amount == Decimal("1234.56")
        assert result.currency == "USD"

    def test_missing_required_field(self):
        """Test mapping fails when required field is missing."""
        mapper = OCRMapper()
        ocr_input = OCRInput(
            extracted_fields={
                "date": "2024-01-15",
                "vendor": "Acme Corp",
                # Missing invoice_number and total
            }
        )

        with pytest.raises(MappingError) as exc_info:
            mapper.map_ocr_to_invoice(ocr_input)

        assert "invoice_number" in str(exc_info.value.details)

    def test_date_parsing(self):
        """Test various date format parsing."""
        mapper = OCRMapper()

        # Test ISO format
        date1 = mapper._parse_date("2024-01-15")
        assert date1.year == 2024
        assert date1.month == 1
        assert date1.day == 15

        # Test US format
        date2 = mapper._parse_date("01/15/2024")
        assert date2.month == 1
        assert date2.day == 15

    def test_decimal_parsing(self):
        """Test various numeric format parsing."""
        mapper = OCRMapper()

        # Test with currency symbol
        amount1 = mapper._parse_decimal("$1,234.56")
        assert amount1 == Decimal("1234.56")

        # Test plain number
        amount2 = mapper._parse_decimal("1234.56")
        assert amount2 == Decimal("1234.56")

        # Test with spaces
        amount3 = mapper._parse_decimal(" 1234.56 ")
        assert amount3 == Decimal("1234.56")

    def test_field_name_variations(self):
        """Test that different field name variations are recognized."""
        mapper = OCRMapper()

        # Test invoice number variations
        ocr_input = OCRInput(
            extracted_fields={
                "inv_no": "INV-001",  # Alternative name
                "date": "2024-01-15",
                "supplier": "Acme Corp",  # Alternative for vendor
                "grand_total": "100.00",  # Alternative for total
            }
        )

        result = mapper.map_ocr_to_invoice(ocr_input)
        assert result.invoice_number == "INV-001"
        assert result.vendor_name == "Acme Corp"
        assert result.total_amount == Decimal("100.00")
