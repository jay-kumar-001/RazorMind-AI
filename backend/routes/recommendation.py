from fastapi import APIRouter
from agents.recommendation_agent import recommendation_agent

router = APIRouter()

@router.get("/recommendations/{merchant_id}")
def get_recommendations(
    merchant_id: str
):

    recommendations = recommendation_agent(
        merchant_id
    )

    return {
        "merchant_id": merchant_id,
        "recommendations": recommendations
    }