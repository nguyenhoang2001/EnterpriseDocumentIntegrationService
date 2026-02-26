"""CRUD operations for database models."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.db.models import Invoice, InvoiceStatus
from app.schemas.invoice import InvoiceCreate
from app.core.exceptions import DatabaseError, NotFoundError


def create_invoice(db: Session, invoice: InvoiceCreate) -> Invoice:
    """Create a new invoice in the database."""
    try:
        db_invoice = Invoice(
            invoice_number=invoice.invoice_number,
            invoice_date=invoice.invoice_date,
            due_date=invoice.due_date,
            vendor_name=invoice.vendor_name,
            vendor_address=invoice.vendor_address,
            vendor_tax_id=invoice.vendor_tax_id,
            customer_name=invoice.customer_name,
            customer_address=invoice.customer_address,
            subtotal=invoice.subtotal,
            tax_amount=invoice.tax_amount,
            total_amount=invoice.total_amount,
            currency=invoice.currency,
            raw_ocr_text=invoice.raw_ocr_text,
            confidence_score=invoice.confidence_score,
            status=InvoiceStatus.PROCESSED,
            processed_at=datetime.utcnow(),
        )
        db.add(db_invoice)
        db.commit()
        db.refresh(db_invoice)
        return db_invoice
    except IntegrityError as e:
        db.rollback()
        raise DatabaseError(
            f"Invoice with number {invoice.invoice_number} already exists",
            details={"error": str(e)},
        )
    except Exception as e:
        db.rollback()
        raise DatabaseError("Failed to create invoice", details={"error": str(e)})


def get_invoice(db: Session, invoice_id: int) -> Invoice:
    """Get invoice by ID."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise NotFoundError(f"Invoice with id {invoice_id} not found")
    return invoice


def get_invoice_by_number(db: Session, invoice_number: str) -> Optional[Invoice]:
    """Get invoice by invoice number."""
    return db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()


def get_invoices(
    db: Session, skip: int = 0, limit: int = 100, status: Optional[InvoiceStatus] = None
) -> List[Invoice]:
    """Get list of invoices with pagination."""
    query = db.query(Invoice)

    if status:
        query = query.filter(Invoice.status == status)

    return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()


def count_invoices(db: Session, status: Optional[InvoiceStatus] = None) -> int:
    """Count total invoices."""
    query = db.query(Invoice)

    if status:
        query = query.filter(Invoice.status == status)

    return query.count()


def update_invoice_status(
    db: Session,
    invoice_id: int,
    status: InvoiceStatus,
    error_message: Optional[str] = None,
) -> Invoice:
    """Update invoice status."""
    invoice = get_invoice(db, invoice_id)
    invoice.status = status
    invoice.error_message = error_message
    invoice.updated_at = datetime.utcnow()

    if status == InvoiceStatus.PROCESSED:
        invoice.processed_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(invoice)
        return invoice
    except Exception as e:
        db.rollback()
        raise DatabaseError(
            "Failed to update invoice status", details={"error": str(e)}
        )


def delete_invoice(db: Session, invoice_id: int) -> None:
    """Delete invoice by ID."""
    invoice = get_invoice(db, invoice_id)
    try:
        db.delete(invoice)
        db.commit()
    except Exception as e:
        db.rollback()
        raise DatabaseError("Failed to delete invoice", details={"error": str(e)})
