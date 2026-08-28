import os
import sys
import numpy as np
import pandas as pd

# Add workspace root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend.database import SessionLocal, engine, Base
from backend.models import Merchant, RevenueForecast, MerchantAnalysis, AgentExecution

COMPANY_NAME_PREFIXES = {
    "Food": ["Zesty", "Urban", "Spice", "Taste", "Fresh", "Gourmet", "Chef", "Bite", "Crisp", "Feast"],
    "SaaS": ["Cloud", "Pulse", "Sync", "Apex", "Nova", "Stream", "Vortex", "Scale", "Stack", "Core"],
    "Gaming": ["Pixel", "Nexus", "Hyper", "Titan", "Rogue", "Arcade", "Shadow", "Cyber", "Quest", "Mythic"],
    "Healthcare": ["Medi", "Care", "Vital", "Bio", "Cure", "Heal", "Life", "Health", "Pulse", "Prime"],
    "Subscription": ["Sub", "Box", "Club", "Pass", "Daily", "Monthly", "Prime", "Access", "Perk", "Elite"],
    "FinTech": ["Pay", "Capital", "Vault", "Mint", "Lend", "Credit", "Coin", "Flow", "Fund", "Ledger"],
    "Travel": ["Voyage", "Trip", "Roam", "Fly", "Wander", "Stay", "Journey", "Compass", "Globe", "Tour"],
    "EdTech": ["Learn", "Skill", "Edu", "Tutor", "Mind", "Study", "Brain", "Course", "Academy", "Scholar"],
    "E-Commerce": ["Store", "Shop", "Cart", "Market", "Bazaar", "Mart", "Trade", "Supply", "Direct", "Hub"]
}

COMPANY_SUFFIXES = ["Labs", "Hub", "Works", "Direct", "Solutions", "Network", "Pay", "Ventures", "Systems", "Technologies"]

def generate_brand_name(merchant_id: str, category: str, city: str) -> str:
    seed = int(merchant_id.replace("M", "")) if merchant_id.startswith("M") and merchant_id[1:].isdigit() else hash(merchant_id) % 10000
    rng = np.random.default_rng(seed)
    prefixes = COMPANY_NAME_PREFIXES.get(category, COMPANY_NAME_PREFIXES["E-Commerce"])
    prefix = rng.choice(prefixes)
    suffix = rng.choice(COMPANY_SUFFIXES)
    return f"{prefix} {suffix} ({city})"

def migrate():
    print("Recreating database tables for updated schema...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS revenue_forecasts CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS merchant_analysis CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS agent_traces CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS merchants CASCADE;"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()


    try:
        print("Loading CSV datasets...")
        kpi_df = pd.read_csv("datasets/merchant_kpis.csv") if os.path.exists("datasets/merchant_kpis.csv") else pd.DataFrame()
        meta_df = pd.read_csv("datasets/merchant_data.csv") if os.path.exists("datasets/merchant_data.csv") else pd.DataFrame()

        if kpi_df.empty:
            print("Error: merchant_kpis.csv not found!")
            return

        merged_df = kpi_df.copy()
        if "category" not in merged_df.columns:
            merged_df["category"] = "E-Commerce"
        if "city" not in merged_df.columns:
            merged_df["city"] = "Mumbai"

        print(f"Migrating {len(merged_df)} merchants into PostgreSQL...")

        for _, row in merged_df.iterrows():
            m_id = str(row["merchant_id"])
            cat = str(row["category"])
            city = str(row["city"])
            brand_name = generate_brand_name(m_id, cat, city)

            total_rev = float(row.get("total_revenue", 100000.0))
            succ_rate = float(row.get("success_rate", 90.0))
            ref_rate = float(row.get("refund_rate", 2.0))
            tot_tx = int(row.get("total_transactions", 500))
            act_cust = int(row.get("active_customers", 300))
            rep_cust = int(row.get("repeat_customers", 50))
            aov = float(row.get("avg_order_value", round(total_rev / max(tot_tx, 1), 2)))
            rev_score = float(row.get("revenue_score", 65.0))
            ret_score = float(row["retention_score"]) if "retention_score" in row and pd.notna(row.get("retention_score")) else float(row.get("retention_rate", 0.0) or 0.0)
            health_score = float(row.get("merchant_health_score", 75.0))
            status = str(row.get("merchant_status", "Healthy"))
            risk_score = float(row.get("risk_score", round(100.0 - health_score, 2)))

            merchant = db.query(Merchant).filter(Merchant.merchant_id == m_id).first()
            if not merchant:
                merchant = Merchant(merchant_id=m_id)
                db.add(merchant)

            merchant.merchant_name = brand_name
            merchant.category = cat
            merchant.industry = f"{cat} Solutions"
            merchant.total_revenue = total_rev
            merchant.total_transactions = tot_tx
            merchant.success_rate = succ_rate
            merchant.refund_rate = ref_rate
            merchant.active_customers = act_cust
            merchant.repeat_customers = rep_cust
            merchant.avg_order_value = aov
            merchant.revenue_score = rev_score
            merchant.retention_score = ret_score
            merchant.risk_score = risk_score
            merchant.merchant_health_score = health_score
            merchant.merchant_status = status

        db.commit()
        print("Merchants migrated successfully!")

        print("Generating comprehensive statistical forecasts for all merchants...")
        db.query(RevenueForecast).delete()

        forecast_records = []
        for _, row in merged_df.iterrows():
            m_id = str(row["merchant_id"])
            base_rev = float(row.get("total_revenue", 100000.0))
            health = float(row.get("merchant_health_score", 75.0))

            # Dynamic monthly growth rate based on health and success
            growth_rate = 0.015 + (health - 50.0) * 0.0008
            noise = np.random.uniform(-0.01, 0.01)

            m1_rev = round(base_rev * (1 + growth_rate + noise), 2)
            m2_rev = round(m1_rev * (1 + growth_rate + noise * 0.8), 2)
            m3_rev = round(m2_rev * (1 + growth_rate + noise * 0.6), 2)

            # 95% Confidence intervals
            volatility = 0.04 if health > 75 else (0.08 if health > 60 else 0.14)

            for i, (m_label, val) in enumerate([("Month+1", m1_rev), ("Month+2", m2_rev), ("Month+3", m3_rev)], 1):
                interval_width = val * volatility * (1 + 0.3 * (i - 1))
                forecast_records.append(
                    RevenueForecast(
                        merchant_id=m_id,
                        forecast_month=m_label,
                        predicted_revenue=val,
                        confidence_lower=round(val - interval_width, 2),
                        confidence_upper=round(val + interval_width, 2),
                        trend_slope=round(growth_rate * 100, 2)
                    )
                )

        db.bulk_save_objects(forecast_records)
        db.commit()
        print(f"Successfully created {len(forecast_records)} dynamic forecasts across all merchants!")

        print("Seeding skipped canned sample analyses — run /analyze/{id} for live briefs.")

    except Exception as e:
        db.rollback()
        print("Migration failed with error:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()