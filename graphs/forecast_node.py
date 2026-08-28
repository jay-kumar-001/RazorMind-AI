import pandas as pd

def forecast_node(state):

    merchant_id = state["merchant_id"]

    df = pd.read_csv(
        "datasets/revenue_forecast.csv"
    )

    forecast = df[
        df["merchant_id"] == merchant_id
    ]

    state["forecast_data"] = (
        forecast.to_dict(
            orient="records"
        )
    )

    return state