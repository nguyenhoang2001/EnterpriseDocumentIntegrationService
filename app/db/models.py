"""SQLAlchemy database models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Enum as SQLEnum
from app.db.session import Base
import enum


class InvoiceStatus(str, enum.Enum):
    """Invoice processing status."""
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class Invoice(Base):
    """Invoice database model."""
    
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Invoice Fields
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=True)
    
    # Vendor Information
    vendor_name = Column(String(255), nullable=False)
    vendor_address = Column(Text, nullable=True)
    vendor_tax_id = Column(String(50), nullable=True)
    
    # Customer Information (if applicable)
    customer_name = Column(String(255), nullable=True)
    customer_address = Column(Text, nullable=True)
    
    # Financial Information
    subtotal = Column(Numeric(10, 2), nullable=True)
    tax_amount = Column(Numeric(10, 2), nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # OCR Source Data
    raw_ocr_text = Column(Text, nullable=True)
    confidence_score = Column(Numeric(5, 2), nullable=True)
    
    # Processing Metadata
    status = Column(
        SQLEnum(InvoiceStatus),
        default=InvoiceStatus.PENDING,
        nullable=False
    )
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, invoice_number='{self.invoice_number}', total={self.total_amount})>"
