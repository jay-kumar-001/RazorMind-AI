import pandas as pd

merchant_df = pd.read_csv(
    "datasets/merchant_kpis.csv"
)

merchant_id = "M0001"

merchant = merchant_df[
    merchant_df["merchant_id"]
    == merchant_id
].iloc[0]

print("\nCURRENT STATE\n")

print(
    merchant[
        [
            "merchant_id",
            "total_revenue",
            "success_rate",
            "refund_rate",
            "merchant_health_score",
            "merchant_status"
        ]
    ]
)

success_rate_change = 5
refund_rate_change = -2

new_success_rate = (
    merchant["success_rate"]
    + success_rate_change
)

new_refund_rate = max(
    0,
    merchant["refund_rate"]
    + refund_rate_change
)

revenue_multiplier = (
    new_success_rate
    /
    merchant["success_rate"]
)

predicted_revenue = (
    merchant["total_revenue"]
    *
    revenue_multiplier
)

predicted_health = min(
    100,
    merchant["merchant_health_score"]
    + success_rate_change * 1.5
)

print("\nSIMULATION RESULT\n")

print(
    f"Predicted Revenue : ₹{predicted_revenue:,.2f}"
)

print(
    f"Predicted Health  : {predicted_health:.2f}"
)

if predicted_health >= 75:
    status = "Healthy"
elif predicted_health >= 60:
    status = "At Risk"
else:
    status = "Critical"

print(
    f"Predicted Status  : {status}"
)
