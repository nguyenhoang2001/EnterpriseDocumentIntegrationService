"""Pydantic schemas for OCR input and invoice output."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class InvoiceStatus(str, Enum):
    """Invoice status enum."""

    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class OCRInput(BaseModel):
    """Schema for raw OCR input data."""

    raw_text: Optional[str] = Field(
        None, description="Raw text extracted from OCR", max_length=50000
    )
    extracted_fields: Dict[str, Any] = Field(
        ..., description="Key-value pairs extracted from OCR"
    )
    confidence_score: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="OCR confidence score (0-100)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "raw_text": "INVOICE\\nInvoice #: INV-2024-001\\nDate: 2024-01-15\\nVendor: Acme Corporation...",
                "extracted_fields": {
                    "invoice_number": "INV-2024-001",
                    "date": "2024-01-15",
                    "vendor": "Acme Corporation",
                    "total": "1234.56",
                },
                "confidence_score": 95.5,
            }
        }
    )


class LineItem(BaseModel):
    """Schema for invoice line item."""

    description: str = Field(..., min_length=1, max_length=500)
    quantity: Decimal = Field(..., gt=0, alias="qty")
    unit_price: Decimal = Field(..., ge=0)
    amount: Decimal = Field(..., ge=0)

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "description": "Professional Services - Consulting",
                "qty": "10",
                "unit_price": "100.00",
                "amount": "1000.00",
            }
        },
    )


class InvoiceCreate(BaseModel):
    """Schema for creating an invoice."""

    invoice_number: str = Field(..., min_length=1, max_length=100)
    invoice_date: datetime
    due_date: Optional[datetime] = None

    vendor_name: str = Field(..., min_length=1, max_length=255)
    vendor_address: Optional[str] = None
    vendor_tax_id: Optional[str] = Field(None, max_length=50)

    customer_name: Optional[str] = Field(None, max_length=255)
    customer_address: Optional[str] = None

    # Line items
    items: Optional[List[LineItem]] = Field(
        None, description="List of invoice line items"
    )

    subtotal: Optional[Decimal] = Field(None, ge=0)
    tax_amount: Optional[Decimal] = Field(None, ge=0)
    total_amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)

    raw_ocr_text: Optional[str] = None
    confidence_score: Optional[Decimal] = Field(None, ge=0, le=100)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code format."""
        return v.upper()

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Validate due date is after invoice date."""
        if v and "invoice_date" in info.data:
            invoice_date = info.data["invoice_date"]
            if v < invoice_date:
                raise ValueError("due_date must be after invoice_date")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "invoice_number": "INV-2024-001",
                "invoice_date": "2024-01-15T00:00:00",
                "due_date": "2024-02-15T00:00:00",
                "vendor_name": "Acme Corporation",
                "vendor_address": "123 Business St, City, State 12345",
                "total_amount": "1234.56",
                "currency": "USD",
            }
        }
    )


class InvoiceResponse(BaseModel):
    """Schema for invoice response."""

    id: int
    invoice_number: str
    invoice_date: datetime
    due_date: Optional[datetime]

    vendor_name: str
    vendor_address: Optional[str]
    vendor_tax_id: Optional[str]

    customer_name: Optional[str]
    customer_address: Optional[str]

    items: Optional[List[LineItem]]

    subtotal: Optional[Decimal]
    tax_amount: Optional[Decimal]
    total_amount: Decimal
    currency: str

    confidence_score: Optional[Decimal]
    status: InvoiceStatus
    error_message: Optional[str]

    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class ProcessingResponse(BaseModel):
    """Schema for OCR processing response."""

    success: bool
    message: str
    invoice: Optional[InvoiceResponse] = None
    errors: Optional[Dict[str, str]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Invoice processed successfully",
                "invoice": {
                    "id": 1,
                    "invoice_number": "INV-2024-001",
                    "total_amount": "1234.56",
                    "status": "processed",
                },
            }
        }
    )


class InvoiceListResponse(BaseModel):
    """Schema for paginated invoice list response."""

    total: int
    skip: int
    limit: int
    invoices: list[InvoiceResponse]

    model_config = ConfigDict(from_attributes=True)
