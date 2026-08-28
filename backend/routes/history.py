from fastapi import APIRouter

from database.db import SessionLocal

from backend.models import MerchantAnalysis

router = APIRouter()


@router.get("/merchant-history/{merchant_id}")
def merchant_history(merchant_id: str):

    db = SessionLocal()

    try:

        analyses = (
            db.query(MerchantAnalysis)
            .filter(
                MerchantAnalysis.merchant_id == merchant_id
            )
            .order_by(
                MerchantAnalysis.id.desc()
            )
            .all()
        )

        result = []

        for item in analyses:

            result.append(
                {
                    "id": item.id,
                    "merchant_id": item.merchant_id,
                    "decision": item.decision,
                    "risk_level": item.risk_level,
                    "created_at": item.created_at
                }
            )

        return result

    finally:

        db.close()