"""Validation service for business rules."""

from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from app.schemas.invoice import InvoiceCreate
from app.core.exceptions import ValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class InvoiceValidator:
    """Validates invoice data against business rules."""

    # Business rules configuration
    MIN_INVOICE_AMOUNT = Decimal("0.01")
    MAX_INVOICE_AMOUNT = Decimal("999999999.99")
    MAX_INVOICE_AGE_DAYS = 365 * 5  # 5 years
    VALID_CURRENCIES = ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CNY"]

    def validate_invoice(self, invoice: InvoiceCreate) -> Dict[str, Any]:
        """
        Validate invoice data against business rules.

        Args:
            invoice: Invoice data to validate

        Returns:
            Dict containing validation results and any warnings

        Raises:
            ValidationError: If validation fails
        """
        errors = []
        warnings = []

        logger.info(
            "Starting invoice validation",
            extra={"invoice_number": invoice.invoice_number},
        )

        # Validate invoice number format
        if not self._validate_invoice_number(invoice.invoice_number):
            errors.append("Invoice number contains invalid characters or format")

        # Validate dates
        date_validation = self._validate_dates(invoice.invoice_date, invoice.due_date)
        errors.extend(date_validation.get("errors", []))
        warnings.extend(date_validation.get("warnings", []))

        # Validate amounts
        amount_validation = self._validate_amounts(
            invoice.total_amount, invoice.subtotal, invoice.tax_amount
        )
        errors.extend(amount_validation.get("errors", []))
        warnings.extend(amount_validation.get("warnings", []))

        # Validate currency
        if not self._validate_currency(invoice.currency):
            errors.append(
                f"Currency '{invoice.currency}' is not supported. Valid currencies: {', '.join(self.VALID_CURRENCIES)}"
            )

        # Validate vendor information
        if not self._validate_vendor_name(invoice.vendor_name):
            errors.append(
                "Vendor name is too short or contains only special characters"
            )

        # Validate confidence score
        if invoice.confidence_score and invoice.confidence_score < 70:
            warnings.append(f"Low OCR confidence score: {invoice.confidence_score}%")

        # Raise validation error if any errors found
        if errors:
            logger.error(
                "Validation failed",
                extra={
                    "invoice_number": invoice.invoice_number,
                    "validation_status": "FAILED",
                    "errors": errors,
                    "warnings": warnings,
                },
            )
            raise ValidationError(
                "Invoice validation failed",
                details={"errors": errors, "warnings": warnings},
            )

        logger.info(
            "Validation passed",
            extra={
                "invoice_number": invoice.invoice_number,
                "validation_status": "PASSED",
                "warnings_count": len(warnings),
                "warnings": warnings,
            },
        )

        return {"valid": True, "validation_status": "PASSED", "warnings": warnings}

    def _validate_invoice_number(self, invoice_number: str) -> bool:
        """Validate invoice number format."""
        if not invoice_number or len(invoice_number.strip()) < 3:
            return False

        # Check if it's not just special characters
        if not any(c.isalnum() for c in invoice_number):
            return False

        return True

    def _validate_dates(
        self, invoice_date: datetime, due_date: Optional[datetime]
    ) -> Dict[str, list]:
        """Validate invoice and due dates."""
        errors = []
        warnings = []
        now = datetime.utcnow()

        # Check if invoice date is too far in the past
        if invoice_date < now - timedelta(days=self.MAX_INVOICE_AGE_DAYS):
            warnings.append(
                f"Invoice date is more than {self.MAX_INVOICE_AGE_DAYS} days old"
            )

        # Check if invoice date is in the future
        if invoice_date > now + timedelta(days=7):
            warnings.append("Invoice date is in the future")

        # Validate due date
        if due_date:
            if due_date < invoice_date:
                errors.append("Due date cannot be before invoice date")

            # Warn if due date is very far in the future
            if due_date > invoice_date + timedelta(days=365):
                warnings.append("Due date is more than 1 year after invoice date")

        return {"errors": errors, "warnings": warnings}

    def _validate_amounts(
        self,
        total_amount: Decimal,
        subtotal: Optional[Decimal],
        tax_amount: Optional[Decimal],
    ) -> Dict[str, list]:
        """Validate financial amounts."""
        errors = []
        warnings = []

        # Validate total amount range
        if total_amount < self.MIN_INVOICE_AMOUNT:
            errors.append(f"Total amount must be at least {self.MIN_INVOICE_AMOUNT}")

        if total_amount > self.MAX_INVOICE_AMOUNT:
            errors.append(f"Total amount cannot exceed {self.MAX_INVOICE_AMOUNT}")

        # Validate amount consistency
        if subtotal and tax_amount:
            calculated_total = subtotal + tax_amount
            difference = abs(calculated_total - total_amount)

            # Allow small rounding differences (up to 0.02)
            if difference > Decimal("0.02"):
                warnings.append(
                    f"Total amount ({total_amount}) doesn't match subtotal + tax ({calculated_total}). "
                    f"Difference: {difference}"
                )

        # Validate subtotal if present
        if subtotal and subtotal < 0:
            errors.append("Subtotal cannot be negative")

        # Validate tax amount if present
        if tax_amount:
            if tax_amount < 0:
                errors.append("Tax amount cannot be negative")

            # Warn if tax seems unusually high (>50% of subtotal)
            if subtotal and tax_amount > (subtotal * Decimal("0.5")):
                warnings.append("Tax amount seems unusually high (>50% of subtotal)")

        return {"errors": errors, "warnings": warnings}

    def _validate_currency(self, currency: str) -> bool:
        """Validate currency code."""
        return currency.upper() in self.VALID_CURRENCIES

    def _validate_vendor_name(self, vendor_name: str) -> bool:
        """Validate vendor name."""
        if not vendor_name or len(vendor_name.strip()) < 2:
            return False

        # Check if it contains at least one alphanumeric character
        if not any(c.isalnum() for c in vendor_name):
            return False

        return True
