import pandas as pd
import numpy as np

print("Loading transactions...")

df = pd.read_csv(
    "datasets/transactions.csv"
)

print("Calculating KPIs...")

merchant_kpis = []

for merchant_id, group in df.groupby("merchant_id"):

    total_transactions = len(group)

    total_revenue = (
        group[group["status"] == "SUCCESS"]["amount"]
        .sum()
    )

    success_rate = (
        (group["status"] == "SUCCESS")
        .mean() * 100
    )

    refund_rate = (
        (group["status"] == "REFUNDED")
        .mean() * 100
    )

    active_customers = (
        group["customer_id"]
        .nunique()
    )

    repeat_customers = (
        group["customer_id"]
        .value_counts()
        .gt(1)
        .sum()
    )

    avg_order_value = (
        group["amount"]
        .mean()
    )

    merchant_kpis.append({

        "merchant_id": merchant_id,

        "total_transactions":
        total_transactions,

        "total_revenue":
        round(total_revenue, 2),

        "success_rate":
        round(success_rate, 2),

        "refund_rate":
        round(refund_rate, 2),

        "active_customers":
        active_customers,

        "repeat_customers":
        repeat_customers,

        "avg_order_value":
        round(avg_order_value, 2)
    })

merchant_df = pd.DataFrame(
    merchant_kpis
)

print("Creating Scores...")

# =====================================
# Revenue Score
# =====================================

merchant_df["revenue_score"] = (

    merchant_df["total_revenue"]

    /

    merchant_df["total_revenue"].max()

) * 100

# =====================================
# Retention Score
# =====================================

merchant_df["retention_score"] = (

    merchant_df["repeat_customers"]

    /

    merchant_df["active_customers"]

) * 100

# =====================================
# Health Score
# =====================================

merchant_df["merchant_health_score"] = (

    merchant_df["success_rate"] * 0.50 +

    merchant_df["retention_score"] * 0.25 +

    merchant_df["revenue_score"] * 0.25

)

# Realistic randomness

merchant_df["merchant_health_score"] += np.random.normal(
    loc=0,
    scale=8,
    size=len(merchant_df)
)

merchant_df["merchant_health_score"] = (

    merchant_df["merchant_health_score"]

    .clip(0, 100)

    .round(2)

)

# =====================================
# Merchant Status
# =====================================

merchant_df["merchant_status"] = pd.qcut(
    merchant_df["merchant_health_score"],
    q=3,
    labels=[
        "Critical",
        "At Risk",
        "Healthy"
    ]
)

# =====================================
# Risk Score
# =====================================

merchant_df["risk_score"] = (
    100 -
    merchant_df["merchant_health_score"]
)

merchant_df["risk_score"] = (
    merchant_df["risk_score"]
    .round(2)
)

# =====================================
# Save File
# =====================================

merchant_df.to_csv(
    "datasets/merchant_kpis.csv",
    index=False
)

# =====================================
# Stats
# =====================================

print("\nMerchant KPI Dataset Generated\n")

print(
    merchant_df.head()
)

print("\nStatus Distribution\n")

print(
    merchant_df["merchant_status"]
    .value_counts()
)

print("\nAverage Health Score")

print(
    merchant_df[
        "merchant_health_score"
    ].mean()
)

print("\nFile Saved")

print(
    "datasets/merchant_kpis.csv"
)