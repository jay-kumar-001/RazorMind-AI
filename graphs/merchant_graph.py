from langgraph.graph import StateGraph, END
from graphs.state import MerchantState
from graphs.nodes import (
    revenue_node,
    forecast_node,
    risk_node,
    churn_node,
    kpi_node,
    rootcause_node,
    recommendation_node,
    decision_node,
    action_plan_node,
    executive_report_node
)

workflow = StateGraph(MerchantState)

# Add Nodes
workflow.add_node("revenue", revenue_node)
workflow.add_node("forecast", forecast_node)
workflow.add_node("risk", risk_node)
workflow.add_node("churn", churn_node)
workflow.add_node("kpi", kpi_node)
workflow.add_node("rootcause", rootcause_node)
workflow.add_node("recommendation", recommendation_node)
workflow.add_node("decision", decision_node)
workflow.add_node("action_plan", action_plan_node)
workflow.add_node("executive_report", executive_report_node)

# Set Entry Point
workflow.set_entry_point("revenue")

# Define Edges
workflow.add_edge("revenue", "forecast")
workflow.add_edge("forecast", "risk")
workflow.add_edge("risk", "churn")
workflow.add_edge("churn", "kpi")
workflow.add_edge("kpi", "rootcause")
workflow.add_edge("rootcause", "recommendation")
workflow.add_edge("recommendation", "decision")
workflow.add_edge("decision", "action_plan")
workflow.add_edge("action_plan", "executive_report")
workflow.add_edge("executive_report", END)

merchant_graph = workflow.compile()