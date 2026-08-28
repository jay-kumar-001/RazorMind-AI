from fastapi import APIRouter

from backend.database import SessionLocal
from backend.models import MerchantAnalysis

router = APIRouter()


@router.get("/merchant-trend/{merchant_id}")
def merchant_trend(merchant_id: str):

    db = SessionLocal()

    try:

        analyses = (
            db.query(MerchantAnalysis)
            .filter(
                MerchantAnalysis.merchant_id == merchant_id
            )
            .order_by(
                MerchantAnalysis.created_at
            )
            .all()
        )

        return {
            "merchant_id": merchant_id,
            "dates": [
                item.created_at.strftime("%Y-%m-%d %H:%M")
                for item in analyses
            ],
            "risk_levels": [
                item.risk_level
                for item in analyses
            ],
            "decisions": [
                item.decision
                for item in analyses
            ]
        }

    finally:
        db.close()