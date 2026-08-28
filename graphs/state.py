from typing import TypedDict, List, Dict, Any, Optional

class MerchantState(TypedDict, total=False):
    merchant_id: str
    revenue_data: Dict[str, Any]
    forecast_data: List[Dict[str, Any]]
    risk_data: Dict[str, Any]
    churn_data: Dict[str, Any]
    kpi_data: Dict[str, Any]
    rootcause_data: Dict[str, Any]
    recommendations: List[str]
    decision_data: Dict[str, Any]
    action_plan: Dict[str, Any]
    executive_report: str
    final_report: Dict[str, Any]
    execution_trace: List[Dict[str, Any]]