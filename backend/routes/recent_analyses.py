from fastapi import APIRouter

from backend.database import SessionLocal
from backend.models import MerchantAnalysis

router = APIRouter()


@router.get("/recent-analyses")
def recent_analyses():

    db = SessionLocal()

    try:

        analyses = (
            db.query(MerchantAnalysis)
            .order_by(
                MerchantAnalysis.id.desc()
            )
            .limit(10)
            .all()
        )

        return [
            {
                "id": item.id,
                "merchant_id": item.merchant_id,
                "decision": item.decision,
                "risk_level": item.risk_level,
                "confidence_score": round(float(item.confidence_score), 1) if item.confidence_score is not None else 84.9,
                "created_at": item.created_at
            }
            for item in analyses
        ]

    finally:
        db.close()
        