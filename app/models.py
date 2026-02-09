from pydantic import BaseModel
from typing import Optional

# Form to create a new account
class AccountCreate(BaseModel):
    owner_name: str                # Customer's name (must be text)
    initial_balance: float = 0.0   # Starting money (defaults to 0)

# Form for deposit/withdrawal
class TransactionRequest(BaseModel):
    amount: float                  # How much money (must be a number)

# Form for transfers
class TransferRequest(BaseModel):
    from_account_id: int           # Sender's account number
    to_account_id: int             # Receiver's account number
    amount: float                  # How much to transfer

# What an account looks like when we show it to someone
class AccountResponse(BaseModel):
    id: int                        # Account number
    owner_name: str                # Customer's name
    balance: float                 # Current balance