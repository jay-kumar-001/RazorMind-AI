import os
from typing import Dict, Any, List

import numpy as np
import pandas as pd

from backend.services.merchant_context import snapshot_metrics, data_confidence


class ChurnService:
    FEATURE_NAMES = [
        "success_rate",
        "refund_rate",
        "retention_score",
        "merchant_health_score",
        "risk_score",
        "total_revenue",
    ]

    def __init__(self):
        self.model_path = "models/churn_model.pkl"
        self._model = None
        self._importances = None
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            return
        try:
            import joblib
            self._model = joblib.load(self.model_path)
            if hasattr(self._model, "feature_importances_"):
                imps = self._model.feature_importances_
                self._importances = {
                    name: round(float(v), 4)
                    for name, v in zip(self.FEATURE_NAMES, imps)
                }
        except Exception:
            self._model = None
            self._importances = None

    def predict_churn(self, merchant: Any) -> Dict[str, Any]:
        success_rate = float(getattr(merchant, "success_rate", 0.0) or 0.0)
        refund_rate = float(getattr(merchant, "refund_rate", 0.0) or 0.0)
        retention_score = float(getattr(merchant, "retention_score", 0.0) or 0.0)
        health_score = float(getattr(merchant, "merchant_health_score", 0.0) or 0.0)
        risk_score = float(getattr(merchant, "risk_score", 0.0) or 0.0)
        total_revenue = float(getattr(merchant, "total_revenue", 0.0) or 0.0)

        used_model = False
        if self._model is not None:
            try:
                features = pd.DataFrame([[
                    success_rate, refund_rate, retention_score,
                    health_score, risk_score, total_revenue
                ]], columns=self.FEATURE_NAMES)
                prob = float(self._model.predict_proba(features)[0, 1]) * 100.0
                used_model = True
            except Exception:
                prob = self._heuristic_churn(health_score, success_rate, refund_rate, retention_score)
        else:
            prob = self._heuristic_churn(health_score, success_rate, refund_rate, retention_score)

        prob = round(max(1.0, min(99.0, prob)), 2)

        if prob >= 65.0:
            churn_risk, urgency = "HIGH", "Critical Retention Alert"
        elif prob >= 35.0:
            churn_risk, urgency = "MEDIUM", "Monitored Retention Alert"
        else:
            churn_risk, urgency = "LOW", "Stable Retention"

        key_drivers: List[str] = []
        if success_rate < 90.0:
            key_drivers.append(f"Checkout declines (success {success_rate:.1f}%)")
        if refund_rate > 2.5:
            key_drivers.append(f"Elevated refunds ({refund_rate:.1f}%)")
        if retention_score < 25.0:
            key_drivers.append(f"Low repeat-buyer index ({retention_score:.1f})")
        if health_score < 60.0:
            key_drivers.append(f"Health drag ({health_score:.1f}/100)")
        if not key_drivers:
            key_drivers.append("Loyalty and processing friction within healthy band")

        if self._importances:
            importance = self._importances
        else:
            importance = {
                "merchant_health_score": 0.35,
                "success_rate": 0.25,
                "refund_rate": 0.20,
                "retention_score": 0.20,
            }

        playbook = (
            "Account-manager outreach + temporary MDR relief + retry routing"
            if prob > 50
            else "Standard QBR cadence; watch auth and refund weekly"
        )
        if success_rate < 90:
            playbook = "Fix authorization leakage first — churn often follows failed checkouts"
        elif refund_rate > 3:
            playbook = "Dispute/refund root-cause before loyalty spend"

        model_name = "RandomForestClassifier" if used_model else "survival_heuristic"
        explanation = (
            f"{model_name} P(churn)={prob:.1f}% ({churn_risk}). "
            f"Drivers: {'; '.join(key_drivers[:3])}."
        )

        return {
            "merchant_id": getattr(merchant, "merchant_id", "Unknown"),
            "churn_probability": prob,
            "churn_risk_level": churn_risk,
            "urgency": urgency,
            "key_drivers": key_drivers,
            "retention_index": retention_score,
            "recommended_playbook": playbook,
            "retention_recommendation": playbook,
            "confidence_score": data_confidence(merchant) if used_model else round(data_confidence(merchant) * 0.9, 1),
            "model": model_name,
            "feature_importance": importance,
            "explanation": explanation,
            "reasoning_summary": explanation,
            "source_metrics": snapshot_metrics(merchant),
        }

    def _heuristic_churn(self, health: float, success: float, refund: float, retention: float) -> float:
        base = (100.0 - health) * 0.55
        if success < 90.0:
            base += (90.0 - success) * 1.2
        if refund > 2.0:
            base += (refund - 2.0) * 3.5
        if retention < 25.0:
            base += (25.0 - retention) * 0.8
        return base


churn_service = ChurnService()
