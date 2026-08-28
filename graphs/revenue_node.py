import pandas as pd

def revenue_node(state):

    merchant_id = state["merchant_id"]

    df = pd.read_csv(
        "datasets/merchant_kpis.csv"
    )

    merchant = df[
        df["merchant_id"] == merchant_id
    ].iloc[0]

    state["revenue_data"] = {
        "revenue":
        merchant["total_revenue"],

        "health_score":
        merchant["merchant_health_score"],

        "status":
        merchant["merchant_status"]
    }

    return state