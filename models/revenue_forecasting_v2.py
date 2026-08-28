import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# =====================================
# LOAD TRANSACTIONS
# =====================================

print("Loading transactions...")

df = pd.read_csv(
    "datasets/transactions.csv"
)

# =====================================
# DATE PROCESSING
# =====================================

df["transaction_date"] = pd.to_datetime(
    df["transaction_date"]
)

# =====================================
# SELECT MERCHANT
# =====================================

merchant_id = "M0001"

merchant_df = df[
    (df["merchant_id"] == merchant_id)
    &
    (df["status"] == "SUCCESS")
]

# =====================================
# MONTHLY REVENUE
# =====================================

monthly_revenue = (

    merchant_df

    .groupby(
        pd.Grouper(
            key="transaction_date",
            freq="ME"
        )
    )

    ["amount"]

    .sum()

    .reset_index()

)

monthly_revenue.columns = [
    "month",
    "revenue"
]

monthly_revenue = (
    monthly_revenue
    .sort_values("month")
    .reset_index(drop=True)
)

# =====================================
# PREPARE TRAINING DATA
# =====================================

monthly_revenue["month_number"] = np.arange(
    1,
    len(monthly_revenue) + 1
)

X = monthly_revenue[
    ["month_number"]
]

y = monthly_revenue[
    "revenue"
]

# =====================================
# TRAIN MODEL
# =====================================

model = LinearRegression()

model.fit(
    X,
    y
)

# =====================================
# FORECAST NEXT 3 MONTHS
# =====================================

future_months = pd.DataFrame({
    "month_number": np.arange(
        len(monthly_revenue) + 1,
        len(monthly_revenue) + 4
    )
})

forecast = model.predict(
    future_months
)

# =====================================
# OUTPUT
# =====================================

print("\n" + "=" * 60)
print("REVENUE FORECAST V2")
print("=" * 60)

print(
    f"Merchant : {merchant_id}"
)

print("\nRecent Revenue History\n")

print(
    monthly_revenue.tail(12)
)

print("\nForecast\n")

print(
    f"Next Month      : ₹{forecast[0]:,.2f}"
)

print(
    f"After 2 Months  : ₹{forecast[1]:,.2f}"
)

print(
    f"After 3 Months  : ₹{forecast[2]:,.2f}"
)

print("=" * 60)

# =====================================
# SAVE FORECAST
# =====================================

forecast_df = pd.DataFrame({

    "merchant_id": [
        merchant_id,
        merchant_id,
        merchant_id
    ],

    "forecast_month": [
        "Month+1",
        "Month+2",
        "Month+3"
    ],

    "predicted_revenue": forecast

})

forecast_df.to_csv(
    "datasets/revenue_forecast.csv",
    index=False
)

print(
    "\nForecast Saved:"
)

print(
    "datasets/revenue_forecast.csv"
)