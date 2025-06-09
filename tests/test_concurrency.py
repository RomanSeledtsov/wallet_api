import uuid
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app import models

client = TestClient(app)

def _create_wallet_in_db(balance: Decimal = Decimal("0")) -> str:
    db = SessionLocal()
    wallet_id = str(uuid.uuid4())
    db.add(models.Wallet(id=wallet_id, balance=balance, is_active=True))
    db.commit()
    db.close()
    return wallet_id

def test_concurrent_withdraws():
    wallet_id = _create_wallet_in_db(balance=Decimal("1000"))

    def withdraw():
        return client.post(
            f"/api/v1/wallets/{wallet_id}/operations",
            json={"operation_type": "WITHDRAW", "amount": 800}
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda fn: fn(), [withdraw, withdraw]))

    statuses = [r.status_code for r in results]
    assert statuses.count(201) == 1
    assert statuses.count(400) == 1

def test_concurrent_deposits():
    wallet_id = _create_wallet_in_db(balance=Decimal("0"))

    def deposit():
        return client.post(
            f"/api/v1/wallets/{wallet_id}/operations",
            json={"operation_type": "DEPOSIT", "amount": 500}
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda fn: fn(), [deposit, deposit]))

    assert all(r.status_code == 201 for r in results)

    resp = client.get(f"/api/v1/wallets/{wallet_id}")
    assert Decimal(resp.json()["balance"]) == Decimal("1000")
