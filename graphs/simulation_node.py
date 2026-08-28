import pandas as pd

def simulation_node(state):

    merchant_id = state["merchant_id"]

    df = pd.read_csv(
        "datasets/merchant_kpis.csv"
    )

    merchant = df[
        df["merchant_id"] ==
        merchant_id
    ].iloc[0]

    current_revenue = float(
        merchant["total_revenue"]
    )

    predicted_revenue = (
        current_revenue * 1.10
    )

    state["simulation_data"] = {

        "current_revenue":
        current_revenue,

        "predicted_revenue":
        predicted_revenue
    }

    return state