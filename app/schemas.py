from pydantic import BaseModel, condecimal
from enum import Enum
from datetime import datetime
from typing import Optional

class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

class WalletBase(BaseModel):
    id: str

class WalletCreate(WalletBase):
    pass

class WalletResponse(WalletBase):
    balance: condecimal(max_digits=12, decimal_places=2)
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

class OperationCreate(BaseModel):
    operation_type: OperationType
    amount: condecimal(gt=0, max_digits=12, decimal_places=2)

class TransactionResponse(BaseModel):
    id: str
    wallet_id: str
    operation_type: str
    amount: condecimal(max_digits=12, decimal_places=2)
    created_at: datetime