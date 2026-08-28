from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from backend.database import get_db

from backend.models import KYCRecord
from backend.models import User

from backend.auth import get_current_user

from backend.schemas import (
    KYCCreate,
    KYCUpdate
)
from backend.services.audit_service import (
    create_audit_log
)

router = APIRouter(
    prefix="/kyc",
    tags=["KYC"]
)


@router.post("/create")
def create_kyc_record(
    payload: KYCCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    kyc = KYCRecord(
        user_id=current_user.id,
        aadhaar_number=payload.aadhaar_number,
        pan_number=payload.pan_number,
        verification_status="pending",
        risk_score=0.0
    )

    db.add(kyc)
    db.commit()
    db.refresh(kyc)
    
    create_audit_log(
    db=db,
    user_id=current_user.id,
    action="KYC_CREATE",
    details=f"KYC submitted with PAN {payload.pan_number}"
    )
    
    return kyc


@router.get("/my")
def get_my_kyc(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return (
        db.query(KYCRecord)
        .filter(
            KYCRecord.user_id == current_user.id
        )
        .all()
    )


@router.get("/{kyc_id}")
def get_kyc(
    kyc_id: int,
    db: Session = Depends(get_db)
):

    kyc = (
        db.query(KYCRecord)
        .filter(
            KYCRecord.id == kyc_id
        )
        .first()
    )

    if not kyc:
        raise HTTPException(
            status_code=404,
            detail="KYC record not found"
        )

    return kyc


@router.put("/{kyc_id}")
def update_kyc(
    kyc_id: int,
    payload: KYCUpdate,
    db: Session = Depends(get_db)
):

    kyc = (
        db.query(KYCRecord)
        .filter(
            KYCRecord.id == kyc_id
        )
        .first()
    )

    if not kyc:
        raise HTTPException(
            status_code=404,
            detail="KYC record not found"
        )

    for key, value in payload.dict(
        exclude_unset=True
    ).items():
        setattr(kyc, key, value)

    db.commit()
    db.refresh(kyc)

    return kyc


@router.delete("/{kyc_id}")
def delete_kyc(
    kyc_id: int,
    db: Session = Depends(get_db)
):

    kyc = (
        db.query(KYCRecord)
        .filter(
            KYCRecord.id == kyc_id
        )
        .first()
    )

    if not kyc:
        raise HTTPException(
            status_code=404,
            detail="KYC record not found"
        )

    db.delete(kyc)
    db.commit()

    return {
        "message": "KYC deleted"
    }
    
