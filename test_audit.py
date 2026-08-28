from backend.database import SessionLocal
from backend.models import AuditLog

db = SessionLocal()

log = AuditLog(
    user_id=1,
    action="TEST",
    details="Manual insert"
)

db.add(log)
db.commit()

print("Inserted")