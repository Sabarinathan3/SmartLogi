"""
SmartLogi – FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import orders, vehicles, predict_delay, optimize_route, sustainability, ai_analysis, empty_mile_api, predictive_dispatch_api

# ─────────────────────────────────────────────
# Application initialisation
# ─────────────────────────────────────────────
app = FastAPI(
    title="SmartLogi API",
    description="AI-powered logistics management backend for SmartLogi",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─────────────────────────────────────────────
# CORS middleware (allow all origins for Flutter)
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Include API routers
# ─────────────────────────────────────────────
app.include_router(orders.router,                  prefix="/api/v1", tags=["Orders"])
app.include_router(vehicles.router,                 prefix="/api/v1", tags=["Vehicles"])
app.include_router(predict_delay.router,            prefix="/api/v1", tags=["AI – Delay Prediction"])
app.include_router(optimize_route.router,           prefix="/api/v1", tags=["AI – Route Optimisation"])
app.include_router(sustainability.router,           prefix="/api/v1", tags=["AI – Sustainability"])
app.include_router(ai_analysis.router,              prefix="/api/v1", tags=["AI – Full Analysis"])
app.include_router(empty_mile_api.router,           prefix="/api/v1", tags=["AI – Empty Mile"])
app.include_router(predictive_dispatch_api.router,  prefix="/api/v1", tags=["AI – Predictive Dispatch"])


# ─────────────────────────────────────────────
# Root health-check endpoint
# ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "app": "SmartLogi API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
