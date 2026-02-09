import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Create a separate TEST database (so tests don't mess up your real data)
TEST_DATABASE_URL = "sqlite:///./test_banking.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# Override get_db to use test database
def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create test database tables
Base.metadata.create_all(bind=test_engine)

# Create the test client
client = TestClient(app)


# ==================== HELPER ====================
def create_test_account(name="Test User", balance=1000):
    response = client.post("/accounts", json={
        "owner_name": name,
        "initial_balance": balance
    })
    return response.json()


# ==================== TESTS ====================

def test_create_account():
    response = client.post("/accounts", json={
        "owner_name": "Raj",
        "initial_balance": 500
    })
    assert response.status_code == 200
    data = response.json()
    assert data["owner_name"] == "Raj"
    assert data["balance"] == 500.0


def test_get_all_accounts():
    response = client.get("/accounts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_account():
    account = create_test_account()
    account_id = account["id"]

    response = client.get(f"/accounts/{account_id}")
    assert response.status_code == 200
    assert response.json()["owner_name"] == "Test User"


def test_account_not_found():
    response = client.get("/accounts/99999")
    assert response.status_code == 404


def test_deposit():
    account = create_test_account(balance=1000)
    account_id = account["id"]

    response = client.post(f"/accounts/{account_id}/deposit", json={
        "amount": 500
    })
    assert response.status_code == 200
    assert response.json()["balance"] == 1500.0


def test_withdraw():
    account = create_test_account(balance=1000)
    account_id = account["id"]

    response = client.post(f"/accounts/{account_id}/withdraw", json={
        "amount": 300
    })
    assert response.status_code == 200
    assert response.json()["balance"] == 700.0


def test_withdraw_insufficient_funds():
    account = create_test_account(balance=100)
    account_id = account["id"]

    response = client.post(f"/accounts/{account_id}/withdraw", json={
        "amount": 500
    })
    assert response.status_code == 400
    assert "Insufficient funds" in response.json()["detail"]


def test_transfer():
    sender = create_test_account(name="Sender", balance=1000)
    receiver = create_test_account(name="Receiver", balance=500)

    response = client.post("/transfer", json={
        "from_account_id": sender["id"],
        "to_account_id": receiver["id"],
        "amount": 300
    })
    assert response.status_code == 200
    assert "Transfer successful" in response.json()["message"]


def test_delete_account():
    account = create_test_account()
    account_id = account["id"]

    response = client.delete(f"/accounts/{account_id}")
    assert response.status_code == 200

    # Verify it's deleted
    response = client.get(f"/accounts/{account_id}")
    assert response.status_code == 404


def test_negative_deposit():
    account = create_test_account()
    account_id = account["id"]

    response = client.post(f"/accounts/{account_id}/deposit", json={
        "amount": -100
    })
    assert response.status_code == 400