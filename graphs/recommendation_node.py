from agents.risk_agent import (
    risk_agent
)

def recommendation_node(state):

    risk_data = state["risk_data"]

    state["recommendations"] = (
        risk_data["recommendations"]
    )

    return state