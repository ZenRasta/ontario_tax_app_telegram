#!/usr/bin/env python3
"""
Backend API Server for DigitalOcean App Platform

This serves only the FastAPI backend routes.
Frontend is served by a separate static site service.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create the main app
app = FastAPI(title="Ontario Tax App API", description="Backend API for Ontario Tax App")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check for the backend service
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ontario-tax-app-backend"}

# Include all routes from the backend app directly into the main app
from backend.app.main import router as backend_router
from backend.app.api.v1.explain import router as explain_router
from backend.app.api.v1.oas_calculator import router as oas_calculator_router

# Mount the main backend router with /v1 prefix for core simulation endpoints
app.include_router(backend_router, prefix="/v1")

# Mount the additional routers directly (they already have /api/v1 prefixes)
app.include_router(explain_router)
app.include_router(oas_calculator_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
