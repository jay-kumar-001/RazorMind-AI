from sqlalchemy.orm import Session

from backend.models import KYCRecord


def create_kyc(
    db: Session,
    user_id: int,
    aadhaar_number: str,
    pan_number: str
):

    kyc = KYCRecord(
        user_id=user_id,
        aadhaar_number=aadhaar_number,
        pan_number=pan_number,
        verification_status="pending",
        risk_score=0.0
    )

    db.add(kyc)
    db.commit()
    db.refresh(kyc)

    return kyc