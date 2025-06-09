from sqlalchemy import Column, String, Numeric, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .database import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    balance = Column(Numeric(scale=2), nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    wallet_id = Column(UUID(as_uuid=True), index=True)
    operation_type = Column(String(10), nullable=False)  # 'DEPOSIT' или 'WITHDRAW'
    amount = Column(Numeric(scale=2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())