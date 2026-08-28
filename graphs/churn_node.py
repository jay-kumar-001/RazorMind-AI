import pandas as pd

def churn_node(state):

    merchant_id = state["merchant_id"]

    df = pd.read_csv(
        "datasets/merchant_predictions.csv"
    )

    merchant = df[
        df["merchant_id"] ==
        merchant_id
    ]

    state["churn_data"] = (
        merchant.to_dict(
            orient="records"
        )
    )

    return state