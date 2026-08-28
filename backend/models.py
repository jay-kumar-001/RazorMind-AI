from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    Boolean,
    ForeignKey
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


# ==========================
# USERS
# ==========================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(500),
        nullable=False
    )

    role = Column(
        String(50),
        default="user"
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    kyc_records = relationship(
        "KYCRecord",
        back_populates="user"
    )

    transactions = relationship(
        "Transaction",
        back_populates="user"
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user"
    )


# ==========================
# KYC RECORDS
# ==========================

class KYCRecord(Base):
    __tablename__ = "kyc_records"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    aadhaar_number = Column(
        String(20)
    )

    pan_number = Column(
        String(20)
    )

    verification_status = Column(
        String(50),
        default="pending"
    )

    risk_score = Column(
        Float,
        default=0.0
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="kyc_records"
    )


# ==========================
# TRANSACTIONS
# ==========================

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    amount = Column(Float)

    transaction_type = Column(
        String(100)
    )

    risk_score = Column(
        Float,
        default=0.0
    )

    status = Column(
        String(50),
        default="pending"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="transactions"
    )

    fraud_alerts = relationship(
        "FraudAlert",
        back_populates="transaction"
    )


# ==========================
# FRAUD ALERTS
# ==========================

class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(
        Integer,
        ForeignKey("transactions.id")
    )

    severity = Column(
        String(50)
    )

    reason = Column(
        Text
    )

    status = Column(
        String(50),
        default="open"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    transaction = relationship(
        "Transaction",
        back_populates="fraud_alerts"
    )


# ==========================
# AGENT EXECUTIONS
# ==========================

class AgentExecution(Base):

    __tablename__ = "agent_executions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    merchant_id = Column(
        String(50)
    )

    agent_name = Column(
        String(255)
    )

    input_query = Column(
        Text
    )

    output_summary = Column(
        Text
    )

    execution_time = Column(
        Float
    )

    status = Column(
        String(50)
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
# ==========================
# AUDIT LOGS
# ==========================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    action = Column(
        String(255)
    )

    details = Column(
        Text
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="audit_logs"
    )


# ==========================
# AI REPORTS
# ==========================

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    report_name = Column(
        String(255)
    )

    report_type = Column(
        String(100)
    )

    file_path = Column(
        String(500)
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    merchant_name = Column(String(255))
    category = Column(String(100), default="E-Commerce")
    industry = Column(String(100), default="Retail")

    total_revenue = Column(Float, default=0.0)
    total_transactions = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    refund_rate = Column(Float, default=0.0)
    active_customers = Column(Integer, default=0)
    repeat_customers = Column(Integer, default=0)
    avg_order_value = Column(Float, default=0.0)
    revenue_score = Column(Float, default=0.0)
    retention_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    merchant_health_score = Column(Float, default=0.0)
    merchant_status = Column(String(50), default="Healthy")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class RevenueForecast(Base):
    __tablename__ = "revenue_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(
        String(50),
        nullable=False,
        index=True
    )
    forecast_month = Column(String(50))
    predicted_revenue = Column(Float)
    confidence_lower = Column(Float, nullable=True)
    confidence_upper = Column(Float, nullable=True)
    trend_slope = Column(Float, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class MerchantAnalysis(Base):
    __tablename__ = "merchant_analysis"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String(50), index=True)
    decision = Column(String(100))
    risk_level = Column(String(50))
    risk_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=95.0)
    executive_report = Column(Text)
    action_plan = Column(Text, nullable=True)
    root_causes = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class AgentTrace(Base):
    __tablename__ = "agent_traces"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String(50), index=True)
    agent_name = Column(String(255))
    execution_time = Column(Float)
    status = Column(String(50), default="SUCCESS")
    details = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )