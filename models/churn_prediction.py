import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# =====================================
# LOAD DATA
# =====================================

df = pd.read_csv(
    "datasets/merchant_kpis.csv"
)

# =====================================
# CREATE CHURN LABEL
# =====================================

def create_churn_label(row):

    if (
        row["merchant_health_score"] < 60
        or (
            row["success_rate"] < 90
            and row["refund_rate"] > 3
        )
    ):
        return 1

    return 0

df["churn"] = df.apply(
    create_churn_label,
    axis=1
)

# =====================================
# FEATURES
# =====================================

X = df[
    [
        "success_rate",
        "refund_rate",
        "retention_score",
        "merchant_health_score",
        "risk_score",
        "total_revenue"
    ]
]

y = df["churn"]

# =====================================
# TRAIN TEST SPLIT
# =====================================

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )
)

# =====================================
# TRAIN MODEL
# =====================================

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42
)

model.fit(
    X_train,
    y_train
)

predictions = model.predict(
    X_test
)

print("\nClassification Report\n")

print(
    classification_report(
        y_test,
        predictions
    )
)

# =====================================
# CHURN PROBABILITY
# =====================================

df["churn_probability"] = (
    model.predict_proba(X)[:, 1]
    * 100
)

df["churn_probability"] = (
    df["churn_probability"]
    .round(2)
)

# =====================================
# SAVE RESULTS
# =====================================

df.to_csv(
    "datasets/merchant_predictions.csv",
    index=False
)

joblib.dump(
    model,
    "models/churn_model.pkl"
)

print(
    "\nPredictions Saved"
)

print(
    "datasets/merchant_predictions.csv"
)

print(
    "\nModel Saved"
)

print(
    "models/churn_model.pkl"
)

# =====================================
# SAMPLE MERCHANT
# =====================================

merchant = df.iloc[0]

print("\n" + "=" * 60)
print("CHURN ANALYSIS")
print("=" * 60)

print(
    f"Merchant ID : {merchant['merchant_id']}"
)

print(
    f"Churn Probability : {merchant['churn_probability']:.2f}%"
)

if merchant["churn_probability"] > 70:
    risk = "HIGH"

elif merchant["churn_probability"] > 40:
    risk = "MEDIUM"

else:
    risk = "LOW"

print(
    f"Risk Level : {risk}"
)

print("=" * 60)