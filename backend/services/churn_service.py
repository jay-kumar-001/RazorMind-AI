import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List

class ChurnService:
    def __init__(self):
        self.model_path = "models/churn_model.pkl"
        self._model = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self._model = joblib.load(self.model_path)
            except Exception:
                self._model = None

    def predict_churn(self, merchant: Any) -> Dict[str, Any]:
        """
        Calculates churn probability and attribution factors for a merchant.
        """
        success_rate = float(getattr(merchant, "success_rate", 92.0) or 92.0)
        refund_rate = float(getattr(merchant, "refund_rate", 1.5) or 1.5)
        retention_score = float(getattr(merchant, "retention_score", 30.0) or 30.0)
        health_score = float(getattr(merchant, "merchant_health_score", 75.0) or 75.0)
        risk_score = float(getattr(merchant, "risk_score", 25.0) or 25.0)
        total_revenue = float(getattr(merchant, "total_revenue", 100000.0) or 100000.0)

        # Feature vector matching training features:
        # ["success_rate", "refund_rate", "retention_score", "merchant_health_score", "risk_score", "total_revenue"]
        if self._model is not None:
            try:
                features = np.array([[
                    success_rate,
                    refund_rate,
                    retention_score,
                    health_score,
                    risk_score,
                    total_revenue
                ]])
                prob = float(self._model.predict_proba(features)[0, 1]) * 100.0
            except Exception:
                prob = self._heuristic_churn(health_score, success_rate, refund_rate, retention_score)
        else:
            prob = self._heuristic_churn(health_score, success_rate, refund_rate, retention_score)

        prob = round(max(1.0, min(99.0, prob)), 2)

        if prob >= 65.0:
            churn_risk = "HIGH"
            urgency = "Critical Retention Alert"
        elif prob >= 35.0:
            churn_risk = "MEDIUM"
            urgency = "Monitored Retention Alert"
        else:
            churn_risk = "LOW"
            urgency = "Stable Retention"

        key_drivers: List[str] = []
        if success_rate < 90.0:
            key_drivers.append(f"Frequent checkout declines (Success Rate: {success_rate:.1f}%)")
        if refund_rate > 2.5:
            key_drivers.append(f"Elevated customer chargebacks/refunds ({refund_rate:.1f}%)")
        if retention_score < 25.0:
            key_drivers.append(f"Low recurring buyer index ({retention_score:.1f}%)")
        if health_score < 60.0:
            key_drivers.append(f"Overall merchant health drag ({health_score:.1f}/100)")
        if not key_drivers:
            key_drivers.append("Strong buyer loyalty and minimal processing friction")

        return {
            "merchant_id": getattr(merchant, "merchant_id", "Unknown"),
            "churn_probability": prob,
            "churn_risk_level": churn_risk,
            "urgency": urgency,
            "key_drivers": key_drivers,
            "retention_index": retention_score,
            "recommended_playbook": (
                "Deploy proactive account manager outreach + rate discount"
                if prob > 50
                else "Maintain standard periodic account reviews"
            )
        }

    def _heuristic_churn(self, health: float, success: float, refund: float, retention: float) -> float:
        # Deterministic formula based on survival analysis curves
        base = (100.0 - health) * 0.55
        if success < 90.0:
            base += (90.0 - success) * 1.2
        if refund > 2.0:
            base += (refund - 2.0) * 3.5
        if retention < 25.0:
            base += (25.0 - retention) * 0.8
        return base

churn_service = ChurnService()
