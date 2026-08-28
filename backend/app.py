from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time

# Core Routes
from backend.routes.merchant import router as merchant_router
from backend.routes.forecast import router as forecast_router
from backend.routes.churn import router as churn_router
from backend.routes.simulate import router as simulation_router
from backend.routes.action_plan import router as action_plan_router
from backend.routes.executive_report import router as executive_router
from backend.routes.decision import router as decision_router
from backend.routes.copilot import router as copilot_router
from backend.routes.rootcause import router as rootcause_router
from backend.routes.recommendation import router as recommendation_router
from backend.routes.dashboard import router as dashboard_router
from backend.routes.recent_analyses import router as recent_router
from backend.routes.merchant_trend import router as trend_router
from backend.routes.history import router as history_router
from backend.routes.analyze import router as analyze_router
from backend.routes.traces import router as traces_router
from backend.routes.langgraph_routes import router as langgraph_router
from backend.routes.graph_analysis import router as graph_router
from backend.routes.pdf_report import router as pdf_router
from backend.routes.auth_routes import router as auth_router
from backend.routes.kyc import router as kyc_router
from backend.routes.intelligence import router as intelligence_router
from backend.routes.transactions import router as transaction_router

app = FastAPI(
    title="RazorMind AI — Enterprise Merchant Intelligence Platform",
    description="Production-grade AI risk underwriting, digital twin simulation, and multi-agent portfolio analytics.",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "RazorMind AI Platform",
        "version": "2.0.0",
        "timestamp": time.time()
    }

@app.get("/health")
def health_check():
    db_status = "disconnected"
    try:
        from backend.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error:{type(e).__name__}"
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "graph": "merchant_graph",
        "version": "2.1.0",
    }

# Register clean non-conflicting routers
app.include_router(merchant_router)
app.include_router(forecast_router)
app.include_router(churn_router)
app.include_router(simulation_router)
app.include_router(action_plan_router)
app.include_router(executive_router)
app.include_router(decision_router)
app.include_router(copilot_router)
app.include_router(rootcause_router)
app.include_router(recommendation_router)
app.include_router(dashboard_router)
app.include_router(recent_router)
app.include_router(trend_router)
app.include_router(history_router)
app.include_router(analyze_router)
app.include_router(traces_router)
app.include_router(langgraph_router)
app.include_router(graph_router)
app.include_router(pdf_router)
app.include_router(auth_router)
app.include_router(kyc_router)
app.include_router(transaction_router)
app.include_router(intelligence_router)
