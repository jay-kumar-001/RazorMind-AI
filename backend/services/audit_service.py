from sqlalchemy.orm import Session

from backend.models import AuditLog


def create_audit_log(
    db: Session,
    user_id: int,
    action: str,
    details: str
):

    log = AuditLog(
        user_id=user_id,
        action=action,
        details=details
    )

    db.add(log)
    db.commit()

    return log