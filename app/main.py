import uuid

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from . import models, schemas, database

app = FastAPI()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        tb = traceback.format_exc()
        print(f"Exception during request: {tb}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


models.Base.metadata.create_all(bind=database.engine)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Wallet API is running"}


@app.post("/api/v1/wallets/{wallet_id}/operations", status_code=status.HTTP_201_CREATED)
def create_operation(wallet_id: str, operation: schemas.OperationCreate,
                     db: Session = Depends(get_db)):
    try:
        wallet_uuid = uuid.UUID(wallet_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid wallet ID")

    try:
        wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).with_for_update().first()
        # Блок записи на время транзакции
        if wallet is None:
            raise HTTPException(status_code=404, detail="Wallet not found")

        if not wallet.is_active:
            raise HTTPException(status_code=400, detail="Wallet is not active")

        if operation.operation_type == schemas.OperationType.WITHDRAW:
            if wallet.balance < operation.amount:
                raise HTTPException(status_code=400, detail="Wallet is not enough")
            wallet.balance -= operation.amount
        elif operation.operation_type == schemas.OperationType.DEPOSIT:
            wallet.balance += operation.amount
        else:
            raise HTTPException(status_code=400, detail="Invalid operation type")

        transaction = models.Transaction(
            id=uuid.uuid4(),
            wallet_id=wallet.id,
            operation_type=operation.operation_type.value,
            amount=operation.amount,
        )

        db.add(transaction)
        db.commit()
        db.refresh(wallet)

        return {
            "wallet_id": str(wallet.id),
            "balance": str(wallet.balance),
            "operation_type": operation.operation_type,
            "amount": str(operation.amount),
        }

    except SQLAlchemyError as e:
        print("SQLAlchemyError detail:", e, flush=True)

        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@app.get("/api/v1/wallets/{wallet_id}", response_model=schemas.WalletResponse)
def get_balance(wallet_id: str, db: Session = Depends(get_db)):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return {
        "id": str(wallet.id),
        "balance": wallet.balance,
        "is_active": wallet.is_active,
        "created_at": wallet.created_at,
        "updated_at": wallet.updated_at,
    }
