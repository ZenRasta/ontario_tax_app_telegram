#!/usr/bin/env python3
"""
Full-stack application for DigitalOcean App Platform

This serves both the FastAPI backend routes and static frontend files.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Create the main app
app = FastAPI(title="Ontario Tax App", description="Ontario Tax App - Full Stack")

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
    return {"status": "healthy", "service": "ontario-tax-app"}

# Include all routes from the backend app directly into the main app
from backend.app.main import router as backend_router
from backend.app.api.v1.explain import router as explain_router
from backend.app.api.v1.oas_calculator import router as oas_calculator_router

# Mount the main backend router with /api/v1 prefix for core simulation endpoints
app.include_router(backend_router, prefix="/api/v1")

# Mount the additional routers directly (they already have /api/v1 prefixes)
app.include_router(explain_router)
app.include_router(oas_calculator_router)

# Serve static files from the built frontend
if os.path.exists("frontend/dist"):
    app.mount("/static", StaticFiles(directory="frontend/dist/assets"), name="static")
    
    # Serve the main frontend app for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # If it's an API route, let FastAPI handle it
        if full_path.startswith("api/") or full_path.startswith("health"):
            return {"error": "Not found"}
        
        # For all other routes, serve the frontend
        if os.path.exists(f"frontend/dist/{full_path}"):
            return FileResponse(f"frontend/dist/{full_path}")
        else:
            # Fallback to index.html for SPA routing
            return FileResponse("frontend/dist/index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
