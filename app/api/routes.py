"""API route handlers."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import ValidationError as PydanticValidationError

from app.db.session import get_db
from app.db import crud
from app.db.models import InvoiceStatus
from app.schemas.invoice import (
    OCRInput,
    InvoiceResponse,
    ProcessingResponse,
    InvoiceListResponse,
)
from app.services.mapper import OCRMapper
from app.services.validator import InvoiceValidator
from app.core.exceptions import (
    OCRServiceException,
    ValidationError,
    MappingError,
    NotFoundError,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter()

# Initialize services
mapper = OCRMapper()
validator = InvoiceValidator()


@router.post("/process-ocr", response_model=ProcessingResponse, status_code=201)
async def process_ocr_document(ocr_input: OCRInput, db: Session = Depends(get_db)):
    """
    Process raw OCR data and create an invoice.

    - Maps OCR extracted fields to invoice schema
    - Validates business rules
    - Saves to database
    - Returns created invoice or error details
    """
    try:
        logger.info(
            "Received OCR processing request",
            extra={
                "fields_count": len(ocr_input.extracted_fields),
                "confidence": ocr_input.confidence_score,
            },
        )

        # Step 1: Map OCR data to invoice schema
        invoice_data = mapper.map_ocr_to_invoice(ocr_input)

        # Step 2: Validate invoice data
        validation_result = validator.validate_invoice(invoice_data)

        # Step 3: Save to database
        db_invoice = crud.create_invoice(db, invoice_data)

        logger.info(
            "Successfully processed OCR document",
            extra={
                "invoice_id": db_invoice.id,
                "invoice_number": db_invoice.invoice_number,
            },
        )

        return ProcessingResponse(
            success=True,
            message=f"Invoice {db_invoice.invoice_number} processed successfully",
            invoice=InvoiceResponse.model_validate(db_invoice),
            errors=None,
        )

    except MappingError as e:
        logger.error("Mapping error", extra={"error": str(e), "details": e.details})
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "message": e.message,
                "invoice": None,
                "errors": e.details.get("field_errors", {}),
            },
        )

    except ValidationError as e:
        logger.error("Validation error", extra={"error": str(e), "details": e.details})
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "message": e.message,
                "invoice": None,
                "errors": e.details,
            },
        )

    except OCRServiceException as e:
        logger.error("Service error", extra={"error": str(e), "details": e.details})
        raise HTTPException(status_code=e.status_code, detail=e.message)

    except PydanticValidationError as e:
        logger.error("Pydantic validation error", extra={"error": str(e)})
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "message": "Validation failed",
                "invoice": None,
                "errors": {"validation": str(e)},
            },
        )

    except Exception as e:
        logger.error("Unexpected error processing OCR", extra={"error": str(e)})
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the document",
        )


@router.get("/invoices", response_model=InvoiceListResponse)
async def get_invoices(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        50, ge=1, le=100, description="Maximum number of records to return"
    ),
    status: Optional[str] = Query(
        None, description="Filter by status: pending, processed, failed"
    ),
    db: Session = Depends(get_db),
):
    """
    Get list of invoices with pagination.

    - Supports pagination via skip/limit
    - Optional status filtering
    - Returns total count and invoice list
    """
    try:
        # Parse status filter
        status_filter = None
        if status:
            try:
                status_filter = InvoiceStatus(status.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status: {status}. Valid values: pending, processed, failed",
                )

        # Get invoices and total count
        invoices = crud.get_invoices(db, skip=skip, limit=limit, status=status_filter)
        total = crud.count_invoices(db, status=status_filter)

        logger.info(
            "Retrieved invoices",
            extra={
                "count": len(invoices),
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )

        return InvoiceListResponse(
            total=total,
            skip=skip,
            limit=limit,
            invoices=[InvoiceResponse.model_validate(inv) for inv in invoices],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving invoices", extra={"error": str(e)})
        raise HTTPException(
            status_code=500, detail="An error occurred while retrieving invoices"
        )


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """
    Get a specific invoice by ID.

    - Returns invoice details
    - Returns 404 if invoice not found
    """
    try:
        invoice = crud.get_invoice(db, invoice_id)

        logger.info(
            "Retrieved invoice",
            extra={"invoice_id": invoice_id, "invoice_number": invoice.invoice_number},
        )

        return InvoiceResponse.model_validate(invoice)

    except NotFoundError as e:
        logger.warning("Invoice not found", extra={"invoice_id": invoice_id})
        raise HTTPException(status_code=404, detail=e.message)

    except Exception as e:
        logger.error(
            "Error retrieving invoice",
            extra={"invoice_id": invoice_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=500, detail="An error occurred while retrieving the invoice"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Enterprise Document Integration Service"}
