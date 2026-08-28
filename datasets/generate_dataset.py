import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# =====================================================
# CONFIG
# =====================================================

NUM_MERCHANTS = 500
NUM_CUSTOMERS = 100000
NUM_TRANSACTIONS = 2000000

np.random.seed(42)

# =====================================================
# MERCHANT DATA
# =====================================================

merchant_ids = [
    f"M{i:04d}"
    for i in range(1, NUM_MERCHANTS + 1)
]

categories = [
    "Ecommerce",
    "EdTech",
    "FinTech",
    "SaaS",
    "Healthcare",
    "Travel",
    "Food",
    "Gaming",
    "Retail",
    "Subscription"
]

cities = [
    "Delhi",
    "Mumbai",
    "Bangalore",
    "Pune",
    "Hyderabad",
    "Chennai",
    "Kolkata",
    "Ahmedabad",
    "Jaipur",
    "Lucknow"
]

merchant_df = pd.DataFrame({
    "merchant_id": merchant_ids,
    "category": np.random.choice(
        categories,
        NUM_MERCHANTS
    ),
    "city": np.random.choice(
        cities,
        NUM_MERCHANTS
    ),
    "created_at": pd.Timestamp.now()
})

# =====================================================
# CUSTOMER DATA
# =====================================================

customer_ids = [
    f"C{i:06d}"
    for i in range(1, NUM_CUSTOMERS + 1)
]

customer_df = pd.DataFrame({
    "customer_id": customer_ids,

    "signup_date":
    pd.to_datetime("2024-01-01") +
    pd.to_timedelta(
        np.random.randint(
            0,
            730,
            NUM_CUSTOMERS
        ),
        unit="D"
    )
})

# =====================================================
# TRANSACTION DATA
# =====================================================

payment_methods = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Wallet",
    "NetBanking",
    "EMI"
]

statuses = [
    "SUCCESS",
    "FAILED",
    "REFUNDED"
]

status_probs = [
    0.90,
    0.07,
    0.03
]

base_date = datetime.now() - timedelta(days=730)

transaction_df = pd.DataFrame({

    "transaction_id": [
        f"T{i:08d}"
        for i in range(
            1,
            NUM_TRANSACTIONS + 1
        )
    ],

    "merchant_id":
    np.random.choice(
        merchant_ids,
        NUM_TRANSACTIONS
    ),

    "customer_id":
    np.random.choice(
        customer_ids,
        NUM_TRANSACTIONS
    ),

    "amount":
    np.round(
        np.random.uniform(
            100,
            10000,
            NUM_TRANSACTIONS
        ),
        2
    ),

    "payment_method":
    np.random.choice(
        payment_methods,
        NUM_TRANSACTIONS
    ),

    "status":
    np.random.choice(
        statuses,
        NUM_TRANSACTIONS,
        p=status_probs
    ),

    "transaction_date":
    pd.to_datetime(base_date) +
    pd.to_timedelta(
        np.random.randint(
            0,
            730,
            NUM_TRANSACTIONS
        ),
        unit="D"
    )
})

# =====================================================
# ADDITIONAL FEATURES
# =====================================================

transaction_df["fee"] = np.round(
    transaction_df["amount"] * 0.02,
    2
)

transaction_df["is_weekend"] = (
    transaction_df["transaction_date"]
    .dt.dayofweek >= 5
)

transaction_df["hour"] = np.random.randint(
    0,
    24,
    NUM_TRANSACTIONS
)

# =====================================================
# SAVE FILES
# =====================================================

merchant_df.to_csv(
    "datasets/merchant_data.csv",
    index=False
)

customer_df.to_csv(
    "datasets/customers.csv",
    index=False
)

transaction_df.to_csv(
    "datasets/transactions.csv",
    index=False
)

# =====================================================
# SUMMARY
# =====================================================

print("\nDATASET GENERATED SUCCESSFULLY\n")

print(
    f"Merchants     : {len(merchant_df):,}"
)

print(
    f"Customers     : {len(customer_df):,}"
)

print(
    f"Transactions  : {len(transaction_df):,}"
)

print(
    f"Total Volume  : ₹{transaction_df['amount'].sum():,.2f}"
)

print(
    f"Success Rate  : "
    f"{(transaction_df['status'] == 'SUCCESS').mean()*100:.2f}%"
)

print(
    "\nFiles Saved:"
)

print("merchant_data.csv")
print("customers.csv")
print("transactions.csv")