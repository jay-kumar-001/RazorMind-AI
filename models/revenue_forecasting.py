import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

# =====================================
# LOAD DATA
# =====================================

merchant_df = pd.read_csv(
    "datasets/merchant_kpis.csv"
)

merchant_id = "M0001"

merchant = merchant_df[
    merchant_df["merchant_id"] == merchant_id
].iloc[0]

# =====================================
# CREATE HISTORICAL REVENUE
# =====================================

current_revenue = merchant[
    "total_revenue"
]

historical_revenue = []

for i in range(12):

    value = current_revenue * (
        0.75 + np.random.random() * 0.35
    )

    historical_revenue.append(value)

months = np.arange(
    1,
    13
).reshape(-1, 1)

revenues = np.array(
    historical_revenue
)

# =====================================
# TRAIN MODEL
# =====================================

model = LinearRegression()

model.fit(
    months,
    revenues
)

# =====================================
# FORECAST
# =====================================

future_months = np.array(
    [13, 14, 15]
).reshape(-1, 1)

forecast = model.predict(
    future_months
)

# =====================================
# OUTPUT
# =====================================

print("\n" + "=" * 60)
print("REVENUE FORECAST")
print("=" * 60)

print(
    f"Merchant : {merchant_id}"
)

print(
    f"Current Revenue : ₹{current_revenue:,.2f}"
)

print("\nForecast\n")

print(
    f"30 Days : ₹{forecast[0]:,.2f}"
)

print(
    f"60 Days : ₹{forecast[1]:,.2f}"
)

print(
    f"90 Days : ₹{forecast[2]:,.2f}"
)

print("=" * 60)