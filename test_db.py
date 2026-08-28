from database.db import engine

try:
    with engine.connect() as conn:
        print("✅ PostgreSQL Connected Successfully")
except Exception as e:
    print("❌ Error:", e)