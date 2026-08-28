def executive_report_node(state):

    state["executive_report"] = (
        executive_report_agent(
            state["revenue_data"],
            state["forecast_data"],
            state["risk_data"],
            state["recommendations"]
        )
    )

    save_analysis(state)

    add_trace(
        state,
        "Executive Report Agent"
    )

    return state
