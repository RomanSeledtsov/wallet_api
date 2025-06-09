import uuid
from decimal import Decimal
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app import models

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

client = TestClient(app)


def _create_wallet_in_db(balance: Decimal = Decimal("0")) -> str:
    """Вспомогательная функция: кладём кошелёк прямо в БД и возвращаем его id."""
    db = SessionLocal()
    wallet_id = str(uuid.uuid4())
    db.add(models.Wallet(id=wallet_id, balance=balance, is_active=True))
    db.commit()
    db.close()
    return wallet_id


def test_full_wallet_flow():
    wallet_id = _create_wallet_in_db()

    # Депозит
    resp = client.post(
        f"/api/v1/wallets/{wallet_id}/operations",
        json={"operation_type": "DEPOSIT", "amount": 1000},
    )
    print("DEPOSIT response status:", resp.status_code)
    print("DEPOSIT response body:", resp.text)
    assert resp.status_code == 201
    assert resp.json()["balance"] == "1000"

    # Снятие
    resp = client.post(
        f"/api/v1/wallets/{wallet_id}/operations",
        json={"operation_type": "WITHDRAW", "amount": 400},
    )
    print("WITHDRAW response status:", resp.status_code)
    print("WITHDRAW response body:", resp.text)
    assert resp.status_code == 201
    assert resp.json()["balance"] == "600"

    # Баланс
    resp = client.get(f"/api/v1/wallets/{wallet_id}")
    print("GET balance response status:", resp.status_code)
    print("GET balance response body:", resp.text)
    assert resp.status_code == 200
    assert resp.json()["balance"] == 600

    # Недостаточно средств
    resp = client.post(
        f"/api/v1/wallets/{wallet_id}/operations",
        json={"operation_type": "WITHDRAW", "amount": 1_000_000},
    )
    print("WITHDRAW too much response status:", resp.status_code)
    print("WITHDRAW too much response body:", resp.text)
    assert resp.status_code == 400
    assert "Wallet is not enough" in resp.text
