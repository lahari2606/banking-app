from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.db_models import Account
from app.models import AccountCreate, TransactionRequest, TransferRequest, AccountResponse

router = APIRouter()


# ==================== CREATE ACCOUNT ====================
@router.post("/accounts", response_model=AccountResponse)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    new_account = Account(
        owner_name=account.owner_name,
        balance=account.initial_balance
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return new_account


# ==================== GET ALL ACCOUNTS ====================
@router.get("/accounts")
def get_all_accounts(db: Session = Depends(get_db)): #gives database connection automatically
    return db.query(Account).all()


# ==================== GET ONE ACCOUNT ====================
@router.get("/accounts/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


# ==================== DEPOSIT ====================
@router.post("/accounts/{account_id}/deposit", response_model=AccountResponse)
def deposit(account_id: int, transaction: TransactionRequest, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive")

    account.balance += transaction.amount
    db.commit()
    db.refresh(account)

    return account


# ==================== WITHDRAW ====================
@router.post("/accounts/{account_id}/withdraw", response_model=AccountResponse)
def withdraw(account_id: int, transaction: TransactionRequest, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be positive")

    if account.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    account.balance -= transaction.amount
    db.commit()
    db.refresh(account)

    return account


# ==================== TRANSFER ====================
@router.post("/transfer")
def transfer(transfer_req: TransferRequest, db: Session = Depends(get_db)):
    sender = db.query(Account).filter(Account.id == transfer_req.from_account_id).first()
    receiver = db.query(Account).filter(Account.id == transfer_req.to_account_id).first()

    if sender is None:
        raise HTTPException(status_code=404, detail="Sender account not found")

    if receiver is None:
        raise HTTPException(status_code=404, detail="Receiver account not found")

    if transfer_req.amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be positive")

    if sender.balance < transfer_req.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    sender.balance -= transfer_req.amount
    receiver.balance += transfer_req.amount
    db.commit()
    db.refresh(sender)
    db.refresh(receiver)

    return {
        "message": "Transfer successful",
        "from_account": {"id": sender.id, "owner_name": sender.owner_name, "balance": sender.balance},
        "to_account": {"id": receiver.id, "owner_name": receiver.owner_name, "balance": receiver.balance}
    }


# ==================== DELETE ACCOUNT ====================
@router.delete("/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    owner_name = account.owner_name
    db.delete(account)
    db.commit()

    return {"message": f"Account {account_id} ({owner_name}) has been closed"}