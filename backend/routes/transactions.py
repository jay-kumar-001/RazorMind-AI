from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.services.audit_service import create_audit_log
from backend.database import get_db
from backend.auth import get_current_user

from backend.models import (
    User,
    Transaction,
    FraudAlert
)

from backend.schemas import (
    TransactionCreate
)
from backend.services.audit_service import (
    create_audit_log
)

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


@router.post("/create")
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    risk_score = 0
    status = "approved"

    # Risk Engine

    if payload.amount > 100000:
        risk_score = 90
        status = "flagged"

    elif payload.amount > 50000:
        risk_score = 60

    transaction = Transaction(
        user_id=current_user.id,
        amount=payload.amount,
        transaction_type=payload.transaction_type,
        risk_score=risk_score,
        status=status
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    create_audit_log(
    db=db,
    user_id=current_user.id,
    action="TRANSACTION_CREATE",
    details=f"Amount: {payload.amount}"
    )
    # Auto Fraud Alert

    if risk_score >= 80:

        alert = FraudAlert(
            transaction_id=transaction.id,
            severity="HIGH",
            reason=f"High amount transaction: INR {payload.amount}",
            status="OPEN"
        )

        db.add(alert)
        db.commit()
        
        create_audit_log(
    db=db,
    user_id=current_user.id,
    action="FRAUD_ALERT",
    details=f"High risk transaction {transaction.id}"
    )
    return transaction


@router.get("/my")
def my_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return (
        db.query(Transaction)
        .filter(
            Transaction.user_id == current_user.id
        )
        .all()
    )