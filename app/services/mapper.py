"""OCR data mapper service - transforms raw OCR output to business schema."""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List
from dateutil import parser as date_parser

from app.schemas.invoice import InvoiceCreate, OCRInput, LineItem
from app.core.exceptions import MappingError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OCRMapper:
    """Maps raw OCR data to structured invoice schema."""

    # Field mapping configuration: OCR field name -> Invoice field name
    FIELD_MAPPINGS = {
        "invoice_number": [
            "invoice_number",
            "invoice_no",
            "inv_no",
            "number",
            "invoice#",
        ],
        "invoice_date": ["invoice_date", "date", "inv_date", "bill_date", "issue_date"],
        "due_date": ["due_date", "payment_due", "due", "payment_date"],
        "vendor_name": [
            "vendor_name",
            "vendor",
            "supplier",
            "from",
            "seller",
            "company",
        ],
        "vendor_address": [
            "vendor_address",
            "vendor_addr",
            "from_address",
            "supplier_address",
        ],
        "vendor_tax_id": ["vendor_tax_id", "tax_id", "vat_number", "ein", "tin"],
        "customer_name": ["customer_name", "customer", "bill_to", "client", "buyer"],
        "customer_address": [
            "customer_address",
            "customer_addr",
            "billing_address",
            "bill_to_address",
        ],
        "subtotal": ["subtotal", "sub_total", "amount", "net_amount"],
        "tax_amount": ["tax_amount", "tax", "vat", "sales_tax"],
        "total_amount": [
            "total_amount",
            "total",
            "grand_total",
            "amount_due",
            "balance_due",
        ],
        "currency": ["currency", "curr", "currency_code"],
    }

    @staticmethod
    def _find_field_value(
        extracted_fields: Dict[str, Any], field_aliases: list[str]
    ) -> Optional[Any]:
        """Find field value from extracted fields using multiple possible keys."""
        for alias in field_aliases:
            # Try exact match (case-insensitive)
            for key, value in extracted_fields.items():
                if key.lower().replace("_", "").replace(
                    " ", ""
                ) == alias.lower().replace("_", "").replace(" ", ""):
                    return value
        return None

    @staticmethod
    def _parse_date(date_value: Any) -> Optional[datetime]:
        """Parse various date formats to datetime."""
        if not date_value:
            return None

        if isinstance(date_value, datetime):
            return date_value

        if isinstance(date_value, str):
            try:
                return date_parser.parse(date_value)
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse date: {date_value}. Error: {str(e)}")
                return None

        return None

    @staticmethod
    def _parse_decimal(value: Any) -> Optional[Decimal]:
        """Parse various numeric formats to Decimal."""
        if not value:
            return None

        if isinstance(value, (int, float, Decimal)):
            return Decimal(str(value))

        if isinstance(value, str):
            # Remove currency symbols and commas
            cleaned = (
                value.replace("$", "")
                .replace("€", "")
                .replace("£", "")
                .replace(",", "")
                .strip()
            )
            try:
                return Decimal(cleaned)
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse decimal: {value}. Error: {str(e)}")
                return None

        return None

    @staticmethod
    def _extract_line_items(
        extracted_fields: Dict[str, Any],
    ) -> Optional[List[LineItem]]:
        """Extract line items from OCR data if present."""
        # Common keys for line items arrays
        line_items_keys = ["items", "line_items", "products", "details", "lines"]

        items_data = None
        for key in line_items_keys:
            items_data = OCRMapper._find_field_value(extracted_fields, [key])
            if items_data:
                break

        if not items_data or not isinstance(items_data, list):
            return None

        line_items = []
        for item_data in items_data:
            if not isinstance(item_data, dict):
                continue

            try:
                # Extract description
                description = (
                    item_data.get("description")
                    or item_data.get("desc")
                    or item_data.get("item")
                    or item_data.get("product")
                    or item_data.get("name")
                    or ""
                )

                # Extract quantity
                qty_raw = (
                    item_data.get("quantity")
                    or item_data.get("qty")
                    or item_data.get("count")
                    or 1
                )
                qty = OCRMapper._parse_decimal(qty_raw)

                # Extract unit price
                unit_price_raw = (
                    item_data.get("unit_price")
                    or item_data.get("price")
                    or item_data.get("rate")
                    or 0
                )
                unit_price = OCRMapper._parse_decimal(unit_price_raw)

                # Extract amount/total
                amount_raw = (
                    item_data.get("amount")
                    or item_data.get("total")
                    or item_data.get("line_total")
                    or 0
                )
                amount = OCRMapper._parse_decimal(amount_raw)

                # Validate required fields
                if (
                    description
                    and qty
                    and qty > 0
                    and unit_price is not None
                    and amount is not None
                ):
                    line_items.append(
                        LineItem(
                            description=str(description)[
                                :500
                            ],  # Truncate to max length
                            qty=qty,
                            unit_price=unit_price,
                            amount=amount,
                        )
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to parse line item: {item_data}. Error: {str(e)}"
                )
                continue

        return line_items if line_items else None

    def map_ocr_to_invoice(self, ocr_input: OCRInput) -> InvoiceCreate:
        """
        Map OCR input to InvoiceCreate schema.

        Args:
            ocr_input: Raw OCR input data

        Returns:
            InvoiceCreate: Structured invoice data

        Raises:
            MappingError: If required fields are missing or invalid
        """
        extracted = ocr_input.extracted_fields
        errors = {}

        logger.info(
            "Starting OCR to Invoice mapping",
            extra={
                "extracted_fields_count": len(extracted),
                "confidence_score": ocr_input.confidence_score,
            },
        )

        # Map invoice number (required)
        invoice_number = self._find_field_value(
            extracted, self.FIELD_MAPPINGS["invoice_number"]
        )
        if not invoice_number:
            errors["invoice_number"] = (
                "Invoice number is required but not found in OCR data"
            )

        # Map invoice date (required)
        invoice_date_raw = self._find_field_value(
            extracted, self.FIELD_MAPPINGS["invoice_date"]
        )
        invoice_date = self._parse_date(invoice_date_raw)
        if not invoice_date:
            errors["invoice_date"] = (
                f"Invoice date is required but not found or invalid: {invoice_date_raw}"
            )

        # Map due date (optional)
        due_date_raw = self._find_field_value(
            extracted, self.FIELD_MAPPINGS["due_date"]
        )
        due_date = self._parse_date(due_date_raw)

        # Map vendor information (required)
        vendor_name = self._find_field_value(
            extracted, self.FIELD_MAPPINGS["vendor_name"]
        )
        if not vendor_name:
            errors["vendor_name"] = "Vendor name is required but not found in OCR data"

        vendor_address = self._find_field_value(
            extracted, self.FIELD_MAPPINGS["vendor_address"]
        )
        vendor_tax_id = self._find_field_value(
            extracted, self.FIELD_MAPPINGS["vendor_tax_id"]
        )

        # Map customer information (optional)
        customer_name = self._find_field_value(
            extracted, self.FIELD_MAPPINGS["customer_name"]
        )
        customer_address = self._find_field_value(
            extracted, self.FIELD_MAPPINGS["customer_address"]
        )

        # Map financial information
        subtotal_raw = self._find_field_value(
            extracted, self.FIELD_MAPPINGS["subtotal"]
        )
        subtotal = self._parse_decimal(subtotal_raw)

        tax_amount_raw = self._find_field_value(
            extracted, self.FIELD_MAPPINGS["tax_amount"]
        )
        tax_amount = self._parse_decimal(tax_amount_raw)

        total_amount_raw = self._find_field_value(
            extracted, self.FIELD_MAPPINGS["total_amount"]
        )
        total_amount = self._parse_decimal(total_amount_raw)
        if not total_amount or total_amount <= 0:
            errors["total_amount"] = (
                f"Total amount is required and must be positive: {total_amount_raw}"
            )

        currency = (
            self._find_field_value(extracted, self.FIELD_MAPPINGS["currency"]) or "USD"
        )

        # Extract line items (optional)
        line_items = self._extract_line_items(extracted)

        # Check for mapping errors
        if errors:
            logger.error("Mapping failed with errors", extra={"errors": errors})
            raise MappingError(
                "Failed to map OCR data to invoice schema",
                details={"field_errors": errors},
            )

        # Create invoice schema
        invoice_data = InvoiceCreate(
            invoice_number=str(invoice_number),
            invoice_date=invoice_date,
            due_date=due_date,
            vendor_name=str(vendor_name),
            vendor_address=str(vendor_address) if vendor_address else None,
            vendor_tax_id=str(vendor_tax_id) if vendor_tax_id else None,
            customer_name=str(customer_name) if customer_name else None,
            customer_address=str(customer_address) if customer_address else None,
            items=line_items,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            currency=str(currency).upper(),
            raw_ocr_text=ocr_input.raw_text,
            confidence_score=(
                Decimal(str(ocr_input.confidence_score))
                if ocr_input.confidence_score
                else None
            ),
        )

        logger.info(
            "Successfully mapped OCR data to invoice",
            extra={
                "invoice_number": invoice_data.invoice_number,
                "total_amount": str(invoice_data.total_amount),
                "line_items_count": len(line_items) if line_items else 0,
            },
        )

        return invoice_data
