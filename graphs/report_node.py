def report_node(state):

    state["final_report"] = {

        "merchant_id":
        state["merchant_id"],

        "forecast":
        state["revenue_forecast"],

        "churn":
        state["churn_data"],

        "simulation":
        state["simulation_data"],

        "recommendations":
        state["recommendations"]

    }

    return state