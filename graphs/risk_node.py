from agents.risk_agent import (
    risk_agent
)

def risk_node(state):

    state["risk_data"] = (
        risk_agent(
            state["merchant_id"]
        )
    )

    return state