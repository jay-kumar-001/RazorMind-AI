#!/usr/bin/env python3
"""
RazorMind AI — Realistic Dataset Generator
Generates reproducible, statistically consistent, and coherent multi-dimensional datasets for 500 merchants:
1. datasets/merchant_kpis.csv
2. datasets/merchant_transactions.csv (50,000 rows)
3. datasets/merchant_customers.csv
4. datasets/merchant_churn.csv
5. datasets/merchant_forecast.csv (calculated mathematically from KPIs)
6. datasets/merchant_risk.csv
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_all_datasets(seed: int = 42, output_dir: str = "datasets"):
    # Set random seeds for exact reproducibility
    random.seed(seed)
    np.random.seed(seed)

    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] Starting RazorMind AI Dataset Generation (Random Seed: {seed})...")

    # -------------------------------------------------------------
    # 1. MERCHANT KPIS GENERATION (500 Unique Merchants: M0001 - M0500)
    # -------------------------------------------------------------
    num_merchants = 500
    merchant_ids = [f"M{i:04d}" for i in range(1, num_merchants + 1)]

    categories = [
        "E-Commerce", "SaaS & Subscriptions", "Fintech & Wealth", 
        "EdTech", "Health & Wellness", "Travel & Hospitality", 
        "Gaming & Entertainment", "D2C Retail", "B2B Logistics", "FoodTech & QSR"
    ]

    company_prefixes = [
        "Apex", "Zenith", "Nova", "Pulse", "Velocity", "Aura", "Quantum", "Nexus", "Hyper", "Vortex",
        "Echo", "Titan", "Aero", "Lumina", "Omni", "Prism", "Stellar", "Core", "Optima", "Vertex",
        "Swift", "Scale", "Elevate", "Sync", "Catalyst", "Beacon", "Flux", "Forge", "Horizon", "Orbit"
    ]
    company_suffixes = [
        "Pay", "Mart", "Tech", "Labs", "Commerce", "Cart", "Cloud", "Solutions", "Dynamics", "Direct",
        "Store", "Ventures", "Systems", "Network", "Hub", "Works", "Platform", "Digital", "Prime", "Wave"
    ]

    used_names = set()
    merchant_names = []
    for _ in range(num_merchants):
        while True:
            name = f"{random.choice(company_prefixes)} {random.choice(company_suffixes)}"
            if name not in used_names:
                used_names.add(name)
                merchant_names.append(name)
                break

    merchants_data = []
    
    # Stratified risk tier assignment:
    # ~55% Low Risk, ~27% Medium Risk, ~13% High Risk, ~5% Critical Risk
    tier_choices = ["LOW"] * 275 + ["MEDIUM"] * 135 + ["HIGH"] * 65 + ["CRITICAL"] * 25
    random.shuffle(tier_choices)

    for i, m_id in enumerate(merchant_ids):
        cat = categories[i % len(categories)]
        name = merchant_names[i]
        tier = tier_choices[i]
        
        # Log-normal distribution for revenue between 100,000 and 50,000,000
        raw_rev = float(np.exp(np.random.uniform(np.log(100000), np.log(50000000))))
        total_revenue = round(float(np.clip(raw_rev, 100000.0, 50000000.0)), 2)

        if tier == "LOW":
            success_rate = round(float(np.clip(np.random.uniform(94.0, 99.8), 70.0, 99.9)), 2)
            refund_rate = round(float(np.clip(np.random.uniform(0.2, 2.0), 0.0, 15.0)), 2)
            chargeback_rate = round(float(np.clip(np.random.uniform(0.02, 0.45), 0.0, 5.0)), 2)
            retention_rate = round(float(np.clip(np.random.uniform(65.0, 96.0), 30.0, 98.0)), 2)
        elif tier == "MEDIUM":
            success_rate = round(float(np.clip(np.random.uniform(86.0, 93.9), 70.0, 99.9)), 2)
            refund_rate = round(float(np.clip(np.random.uniform(2.1, 4.8), 0.0, 15.0)), 2)
            chargeback_rate = round(float(np.clip(np.random.uniform(0.5, 1.4), 0.0, 5.0)), 2)
            retention_rate = round(float(np.clip(np.random.uniform(45.0, 68.0), 30.0, 98.0)), 2)
        elif tier == "HIGH":
            success_rate = round(float(np.clip(np.random.uniform(76.0, 85.9), 70.0, 99.9)), 2)
            refund_rate = round(float(np.clip(np.random.uniform(5.0, 9.5), 0.0, 15.0)), 2)
            chargeback_rate = round(float(np.clip(np.random.uniform(1.5, 3.2), 0.0, 5.0)), 2)
            retention_rate = round(float(np.clip(np.random.uniform(32.0, 48.0), 30.0, 98.0)), 2)
        else:  # CRITICAL
            success_rate = round(float(np.clip(np.random.uniform(70.0, 77.0), 70.0, 99.9)), 2)
            refund_rate = round(float(np.clip(np.random.uniform(9.0, 14.8), 0.0, 15.0)), 2)
            chargeback_rate = round(float(np.clip(np.random.uniform(3.0, 4.9), 0.0, 5.0)), 2)
            retention_rate = round(float(np.clip(np.random.uniform(25.0, 35.0), 20.0, 98.0)), 2)

        # Transactions between 100 and 50,000
        raw_tx_count = int(np.exp(np.random.uniform(np.log(100), np.log(50000))))
        total_transactions = int(np.clip(raw_tx_count, 100, 50000))

        # Derived Average Order Value (AOV)
        avg_order_value = round(total_revenue / total_transactions, 2)

        # Active customers derived from transactions and retention
        active_customers = int(max(50, total_transactions * (1.0 - (retention_rate / 200.0))))

        # Coherent Health Score Calculation (10 to 100)
        succ_factor = (success_rate - 70.0) / 30.0 * 40.0   # 0 to 40 pts
        ret_factor = (retention_rate - 20.0) / 78.0 * 30.0   # 0 to 30 pts
        ref_factor = max(0.0, (15.0 - refund_rate) / 15.0) * 20.0  # 0 to 20 pts
        cb_factor = max(0.0, (5.0 - chargeback_rate) / 5.0) * 10.0  # 0 to 10 pts
        raw_health = succ_factor + ret_factor + ref_factor + cb_factor
        health_score = round(float(np.clip(raw_health, 10.0, 100.0)), 2)

        # Coherent Risk Score (0 to 100)
        raw_risk = (
            (100.0 - success_rate) * 1.5 +
            (refund_rate * 3.5) +
            (chargeback_rate * 8.0) +
            ((100.0 - retention_rate) * 0.25)
        )
        risk_score = round(float(np.clip(raw_risk, 0.0, 100.0)), 2)

        # Risk Level Classification matching tier
        risk_level = tier

        # Merchant Status
        if risk_level == "CRITICAL":
            merchant_status = "RESTRICTED"
        elif risk_level == "HIGH":
            merchant_status = "UNDER_REVIEW"
        else:
            merchant_status = "ACTIVE"

        created_days_ago = random.randint(30, 730)
        created_at = (datetime.now() - timedelta(days=created_days_ago)).strftime("%Y-%m-%d")

        merchants_data.append({
            "merchant_id": m_id,
            "merchant_name": name,
            "category": cat,
            "industry": cat,
            "total_revenue": total_revenue,
            "success_rate": success_rate,
            "refund_rate": refund_rate,
            "chargeback_rate": chargeback_rate,
            "retention_rate": retention_rate,
            "total_transactions": total_transactions,
            "avg_order_value": avg_order_value,
            "active_customers": active_customers,
            "merchant_health_score": health_score,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "merchant_status": merchant_status,
            "created_at": created_at
        })

    df_kpis = pd.DataFrame(merchants_data)
    kpis_path = os.path.join(output_dir, "merchant_kpis.csv")
    df_kpis.to_csv(kpis_path, index=False)
    print(f"[OK] Saved {len(df_kpis)} merchants to '{kpis_path}'")

    # -------------------------------------------------------------
    # 2. CUSTOMERS GENERATION
    # -------------------------------------------------------------
    first_names = ["Aarav", "Aditi", "Rohan", "Priya", "Vikram", "Neha", "Rahul", "Ananya", "Amit", "Pooja",
                   "Karan", "Sneha", "Arjun", "Kavya", "Siddharth", "Meera", "Varun", "Isha", "Nikhil", "Divya"]
    last_names = ["Sharma", "Verma", "Patel", "Mehta", "Gupta", "Singh", "Reddy", "Nair", "Chopra", "Deshmukh",
                  "Iyer", "Joshi", "Kapoor", "Bose", "Rao", "Malhotra", "Saxena", "Bhat", "Kulkarni", "Das"]

    total_unique_customers = 15000
    customers_data = []
    
    for c_idx in range(1, total_unique_customers + 1):
        cust_id = f"CUST_{c_idx:06d}"
        m_id = random.choice(merchant_ids)
        c_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"{c_name.lower().replace(' ', '.')}_{c_idx % 997}@example.com"
        
        m_kpi = df_kpis[df_kpis["merchant_id"] == m_id].iloc[0]
        aov = m_kpi["avg_order_value"]
        
        # Number of orders based on retention rate
        is_repeat = (random.random() * 100.0) < m_kpi["retention_rate"]
        order_count = random.randint(2, 18) if is_repeat else 1
        total_spent = round(float(order_count * aov * np.random.uniform(0.85, 1.25)), 2)
        
        days_first = random.randint(15, 360)
        days_last = random.randint(1, max(1, days_first - 1)) if is_repeat else days_first
        first_date = (datetime.now() - timedelta(days=days_first)).strftime("%Y-%m-%d")
        last_date = (datetime.now() - timedelta(days=days_last)).strftime("%Y-%m-%d")
        
        if total_spent > aov * 10:
            loyalty_tier = "PLATINUM"
        elif total_spent > aov * 4:
            loyalty_tier = "GOLD"
        elif total_spent > aov * 2:
            loyalty_tier = "SILVER"
        else:
            loyalty_tier = "STANDARD"

        customers_data.append({
            "customer_id": cust_id,
            "merchant_id": m_id,
            "customer_name": c_name,
            "email": email,
            "total_orders": order_count,
            "total_spent": total_spent,
            "first_order_date": first_date,
            "last_order_date": last_date,
            "is_repeat_customer": is_repeat,
            "loyalty_tier": loyalty_tier
        })

    df_customers = pd.DataFrame(customers_data)
    customers_path = os.path.join(output_dir, "merchant_customers.csv")
    df_customers.to_csv(customers_path, index=False)
    print(f"[OK] Saved {len(df_customers)} customers to '{customers_path}'")

    # -------------------------------------------------------------
    # 3. TRANSACTIONS GENERATION (50,000 Transactions)
    # -------------------------------------------------------------
    total_target_tx = 50000
    payment_methods = ["UPI", "CREDIT_CARD", "DEBIT_CARD", "NET_BANKING", "WALLET", "EMI"]
    payment_weights = [0.48, 0.24, 0.14, 0.08, 0.04, 0.02]

    # Assign transactions proportionally across merchants based on total_transactions
    tx_weights = df_kpis["total_transactions"].values / df_kpis["total_transactions"].sum()
    tx_counts_per_merchant = np.random.multinomial(total_target_tx, tx_weights)

    # Pre-index customer IDs per merchant for speed
    merchant_cust_map = df_customers.groupby("merchant_id")["customer_id"].apply(list).to_dict()

    transactions_data = []
    tx_counter = 1

    start_date = datetime.now() - timedelta(days=90)

    for i, m_id in enumerate(merchant_ids):
        m_kpi = df_kpis.iloc[i]
        count_for_m = tx_counts_per_merchant[i]
        if count_for_m == 0:
            continue

        succ_p = m_kpi["success_rate"] / 100.0
        ref_p = (m_kpi["refund_rate"] / 100.0) * succ_p
        fail_p = max(0.001, 1.0 - succ_p)
        succ_actual_p = max(0.001, succ_p - ref_p)
        
        # Normalize status probabilities
        tot_p = succ_actual_p + fail_p + ref_p
        p_succ = succ_actual_p / tot_p
        p_fail = fail_p / tot_p
        p_ref = ref_p / tot_p

        statuses = np.random.choice(["SUCCESS", "FAILED", "REFUNDED"], size=count_for_m, p=[p_succ, p_fail, p_ref])
        p_methods = np.random.choice(payment_methods, size=count_for_m, p=payment_weights)
        
        aov = m_kpi["avg_order_value"]
        cust_list = merchant_cust_map.get(m_id, [f"CUST_ANON_{m_id}"])

        for t_idx in range(count_for_m):
            status = statuses[t_idx]
            pm = p_methods[t_idx]
            c_id = random.choice(cust_list)
            
            # Log-normal variation around AOV
            amount = round(float(np.clip(np.random.lognormal(np.log(max(10.0, aov)), 0.45), 50.0, 500000.0)), 2)
            
            # Fee calculation (Razorpay standard 1.5% - 2.5%)
            fee_rate = 0.015 if pm == "UPI" else 0.022
            fee = round(amount * fee_rate, 2)

            # Random timestamp in past 90 days
            tx_time = start_date + timedelta(
                seconds=random.randint(0, int(90 * 86400))
            )
            
            # Risk flag for abnormal transactions
            is_risk = (status == "FAILED" and amount > aov * 3) or (m_kpi["risk_level"] == "HIGH" and random.random() < 0.20)

            transactions_data.append({
                "transaction_id": f"TXN_{tx_counter:07d}",
                "merchant_id": m_id,
                "customer_id": c_id,
                "amount": amount,
                "currency": "INR",
                "status": status,
                "payment_method": pm,
                "fee": fee,
                "risk_flag": is_risk,
                "created_at": tx_time.strftime("%Y-%m-%d %H:%M:%S")
            })
            tx_counter += 1

    df_transactions = pd.DataFrame(transactions_data)
    transactions_path = os.path.join(output_dir, "merchant_transactions.csv")
    df_transactions.to_csv(transactions_path, index=False)
    print(f"[OK] Saved {len(df_transactions)} transactions to '{transactions_path}'")

    # -------------------------------------------------------------
    # 4. CHURN ANALYSIS GENERATION (500 Merchants)
    # -------------------------------------------------------------
    churn_drivers = [
        "Payment Gateway Failures & Bank Latency",
        "Elevated Return/Refund Volume",
        "Competitor Price Undercutting",
        "Checkout Funnel Friction",
        "Seasonal Demand Drop",
        "Product Catalog Fatigue",
        "Lack of Re-engagement Campaigns"
    ]

    churn_data = []
    for _, row in df_kpis.iterrows():
        m_id = row["merchant_id"]
        ret = row["retention_rate"]
        health = row["merchant_health_score"]
        
        # Mathematical churn probability derived from retention and health
        base_churn = (100.0 - ret) / 100.0
        health_penalty = max(0.0, (75.0 - health) / 100.0) * 0.3
        churn_prob = round(float(np.clip(base_churn * 0.7 + health_penalty + np.random.uniform(-0.05, 0.05), 0.02, 0.95)), 4)

        if churn_prob < 0.25:
            churn_level = "LOW"
        elif churn_prob < 0.60:
            churn_level = "MEDIUM"
        else:
            churn_level = "HIGH"

        inactive_days = int(np.clip((100 - health) * 0.8 + np.random.uniform(1, 15), 1, 90))
        rev_decline = round(float(np.clip((100 - ret) * 0.45 + (100 - health) * 0.35 + np.random.uniform(-5, 5), -15.0, 65.0)), 2)
        reorder_drop = round(float(np.clip((100 - ret) * 0.6 + np.random.uniform(-4, 6), 0.0, 75.0)), 2)
        open_tickets = int(max(0, round((100 - health) * 0.15 + np.random.uniform(0, 4))))
        
        driver = random.choice(churn_drivers) if churn_level != "LOW" else "Normal Healthy Velocity"

        if churn_level == "HIGH":
            recom = "Deploy urgent automated checkout retry logic, instant WhatsApp refund notifications, and 15% win-back incentives."
        elif churn_level == "MEDIUM":
            recom = "Enable dynamic gateway routing and launch personalized re-engagement sequence."
        else:
            recom = "Maintain current customer loyalty programs and test VIP tiers."

        churn_data.append({
            "merchant_id": m_id,
            "churn_probability": churn_prob,
            "churn_risk_level": churn_level,
            "inactive_days": inactive_days,
            "revenue_decline_pct": rev_decline,
            "reorder_drop_pct": reorder_drop,
            "support_tickets_open": open_tickets,
            "churn_driver": driver,
            "retention_recommendation": recom
        })

    df_churn = pd.DataFrame(churn_data)
    churn_path = os.path.join(output_dir, "merchant_churn.csv")
    df_churn.to_csv(churn_path, index=False)
    print(f"[OK] Saved {len(df_churn)} churn records to '{churn_path}'")

    # -------------------------------------------------------------
    # 5. FORECAST DATA GENERATION (Calculated statistically from KPIs)
    # -------------------------------------------------------------
    forecast_data = []
    for _, row in df_kpis.iterrows():
        m_id = row["merchant_id"]
        annual_rev = row["total_revenue"]
        monthly_base = annual_rev / 12.0
        health = row["merchant_health_score"]
        succ = row["success_rate"]
        ret = row["retention_rate"]

        # Dynamic monthly growth rate driven by health, retention, and success rate
        growth_rate = ((health - 65.0) * 0.003) + ((ret - 50.0) * 0.002) + np.random.uniform(-0.015, 0.025)
        growth_trend_pct = round(growth_rate * 100.0, 2)

        # Month 1 (+30 Days)
        m1_rev = round(monthly_base * (1.0 + growth_rate), 2)
        m1_low = round(m1_rev * (0.92 - (100 - succ) * 0.003), 2)
        m1_high = round(m1_rev * (1.08 + (succ - 70) * 0.002), 2)

        # Month 2 (+60 Days)
        m2_rev = round(m1_rev * (1.0 + growth_rate * 1.05), 2)
        m2_low = round(m2_rev * (0.88 - (100 - succ) * 0.004), 2)
        m2_high = round(m2_rev * (1.12 + (succ - 70) * 0.003), 2)

        # Month 3 (+90 Days)
        m3_rev = round(m2_rev * (1.0 + growth_rate * 1.10), 2)
        m3_low = round(m3_rev * (0.84 - (100 - succ) * 0.005), 2)
        m3_high = round(m3_rev * (1.16 + (succ - 70) * 0.004), 2)

        confidence_pct = round(float(np.clip(70.0 + (health * 0.25) + np.random.uniform(-2.0, 3.0), 65.0, 98.0)), 1)

        forecast_data.append({
            "merchant_id": m_id,
            "historical_monthly_revenue": round(monthly_base, 2),
            "growth_trend_pct": growth_trend_pct,
            "forecast_m1_revenue": m1_rev,
            "forecast_m1_lower": m1_low,
            "forecast_m1_upper": m1_high,
            "forecast_m2_revenue": m2_rev,
            "forecast_m2_lower": m2_low,
            "forecast_m2_upper": m2_high,
            "forecast_m3_revenue": m3_rev,
            "forecast_m3_lower": m3_low,
            "forecast_m3_upper": m3_high,
            "forecast_confidence_pct": confidence_pct
        })

    df_forecast = pd.DataFrame(forecast_data)
    forecast_path = os.path.join(output_dir, "merchant_forecast.csv")
    df_forecast.to_csv(forecast_path, index=False)
    print(f"[OK] Saved {len(df_forecast)} forecast profiles to '{forecast_path}'")

    # -------------------------------------------------------------
    # 6. RISK ASSESSMENT GENERATION (500 Merchants)
    # -------------------------------------------------------------
    risk_data = []
    for _, row in df_kpis.iterrows():
        m_id = row["merchant_id"]
        risk_score = row["risk_score"]
        risk_lvl = row["risk_level"]
        succ = row["success_rate"]
        ref = row["refund_rate"]
        cb = row["chargeback_rate"]
        ret = row["retention_rate"]

        failure_risk = round(float(np.clip((100.0 - succ) * 3.0, 0.0, 100.0)), 2)
        dispute_risk = round(float(np.clip((ref * 4.5) + (cb * 12.0), 0.0, 100.0)), 2)
        volatility_risk = round(float(np.clip((100.0 - ret) * 0.8 + np.random.uniform(5, 15), 5.0, 95.0)), 2)
        churn_risk = round(float(np.clip((100.0 - ret) * 0.9 + np.random.uniform(0, 10), 0.0, 100.0)), 2)

        if risk_lvl == "LOW":
            decision = "APPROVE"
            priority = "STANDARD_MONITORING"
            flag = "Healthy Operational Flow"
        elif risk_lvl == "MEDIUM":
            decision = "APPROVE_WITH_MONITORING" if risk_score < 50.0 else "MONITOR_CLOSELY"
            priority = "ELEVATED_WATCH"
            flag = "Moderate Settlement / Return Volatility"
        elif risk_lvl == "HIGH":
            decision = "ENHANCED_DUE_DILIGENCE"
            priority = "HIGH_PRIORITY_AUDIT"
            flag = "Severe Decline / Dispute Concentration"
        else:  # CRITICAL
            decision = "MANUAL_INTERVENTION_REQUIRED"
            priority = "IMMEDIATE_TERMINATION_OR_REMEDY"
            flag = "Critical Fraud / Chargeback Threshold Breach"

        risk_data.append({
            "merchant_id": m_id,
            "risk_score": risk_score,
            "risk_level": risk_lvl,
            "failure_risk_score": failure_risk,
            "dispute_risk_score": dispute_risk,
            "volatility_risk_score": volatility_risk,
            "churn_risk_score": churn_risk,
            "underwriting_decision": decision,
            "monitoring_priority": priority,
            "primary_risk_flag": flag
        })

    df_risk = pd.DataFrame(risk_data)
    risk_path = os.path.join(output_dir, "merchant_risk.csv")
    df_risk.to_csv(risk_path, index=False)
    print(f"[OK] Saved {len(df_risk)} risk profiles to '{risk_path}'")

    # -------------------------------------------------------------
    # SUMMARY OUTPUT
    # -------------------------------------------------------------
    print("\n" + "=" * 60)
    print("RAZORMIND AI -- DATASET GENERATION COMPLETE")
    print("=" * 60)
    print(f"total merchants:    {len(df_kpis)}")
    print(f"total transactions: {len(df_transactions)}")
    print(f"total customers:    {len(df_customers)}")
    print("=" * 60)
    print(f"Files generated inside '{output_dir}/':")
    print(f" 1. {kpis_path} ({len(df_kpis)} rows)")
    print(f" 2. {transactions_path} ({len(df_transactions)} rows)")
    print(f" 3. {customers_path} ({len(df_customers)} rows)")
    print(f" 4. {churn_path} ({len(df_churn)} rows)")
    print(f" 5. {forecast_path} ({len(df_forecast)} rows)")
    print(f" 6. {risk_path} ({len(df_risk)} rows)")
    print("=" * 60 + "\n")

    return {
        "merchants": len(df_kpis),
        "transactions": len(df_transactions),
        "customers": len(df_customers)
    }

if __name__ == "__main__":
    generate_all_datasets()
