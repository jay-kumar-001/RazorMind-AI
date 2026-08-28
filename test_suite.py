import os
import sys

# Ensure root directory is on PATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("RAZORMIND AI — FULL SUITE VERIFICATION")
    print("=" * 60)

    # 1. Health check
    res = client.get("/health")
    print("[1/12] GET /health ->", res.status_code, res.json())
    assert res.status_code == 200

    # 2. Portfolio Dashboard
    res = client.get("/dashboard")
    print("[2/12] GET /dashboard ->", res.status_code, "Total merchants:", res.json().get("total_merchants"))
    assert res.status_code == 200

    # 3. Merchant Detail
    res = client.get("/merchant/M0001")
    print("[3/12] GET /merchant/M0001 ->", res.status_code, "Health:", res.json().get("merchant_health_score"))
    assert res.status_code == 200

    # 4. Merchant Forecast
    res = client.get("/merchant/M0001/forecast")
    print("[4/12] GET /merchant/M0001/forecast ->", res.status_code, "Forecast points:", len(res.json()))
    assert res.status_code == 200
    assert len(res.json()) >= 3

    # 5. Merchant Churn
    res = client.get("/merchant/M0001/churn")
    print("[5/12] GET /merchant/M0001/churn ->", res.status_code, "Churn prob:", res.json().get("churn_probability"))
    assert res.status_code == 200

    # 6. Digital Twin Simulation
    sim_payload = {
        "merchant_id": "M0001",
        "success_rate_increase": 4.0,
        "refund_rate_reduction": 1.0,
        "churn_rate_reduction": 2.0,
        "retention_increase": 5.0,
        "volume_growth": 10.0
    }
    res = client.post("/simulate", json=sim_payload)
    print("[6/12] POST /simulate ->", res.status_code, "Simulated Rev Lift:", res.json().get("simulated", {}).get("revenue_growth_percent"), "%")
    assert res.status_code == 200

    # 7. Action Plan
    res = client.get("/action-plan/M0001")
    print("[7/12] GET /action-plan/M0001 ->", res.status_code, "Risk Level:", res.json().get("risk_level"))
    assert res.status_code == 200

    # 8. Underwriting Decision
    res = client.get("/decision/M0001")
    print("[8/12] GET /decision/M0001 ->", res.status_code, "Decision:", res.json().get("final_decision"))
    assert res.status_code == 200

    # 9. Root Cause Analysis
    res = client.get("/merchant/M0001/root-cause")
    print("[9/12] GET /merchant/M0001/root-cause ->", res.status_code, "Bottleneck:", res.json().get("primary_bottleneck"))
    assert res.status_code == 200

    # 10. Observability Traces
    res = client.get("/agent-traces/M0001")
    print("[10/12] GET /agent-traces/M0001 ->", res.status_code, "Trace records:", len(res.json()))
    assert res.status_code == 200

    # 11. Executive Report
    res = client.get("/executive-report/M0001")
    print("[11/12] GET /executive-report/M0001 ->", res.status_code, "Confidence:", res.json().get("confidence_score"))
    assert res.status_code == 200

    # 12. Copilot Query
    res = client.get("/copilot/M0001?question=What is the primary risk driver for this merchant?")
    print("[12/12] GET /copilot/M0001 ->", res.status_code, "Answer received length:", len(res.json().get("answer", "")))
    assert res.status_code == 200

    print("=" * 60)
    print("ALL 12 BACKEND ENDPOINTS AND AGENT PIPELINES PASSED PERFECTLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
