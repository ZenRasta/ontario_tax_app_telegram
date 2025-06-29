#!/usr/bin/env python3
"""
Combined FastAPI + Static File Server for DigitalOcean App Platform

This serves:
- FastAPI backend at /api/* routes (backend app has /api/v1 prefix internally)
- Frontend static files for all other routes
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import the backend FastAPI app
from backend.app.main import app as backend_app

# Create the main app
app = FastAPI(title="Ontario Tax App", description="Combined Frontend + Backend")

# Determine the frontend build directory
frontend_build_dir = Path("frontend/dist")
if not frontend_build_dir.exists():
    # Fallback to development structure
    frontend_build_dir = Path("frontend/public")

# Mount static files only if they exist
if frontend_build_dir.exists():
    # Check if assets directory exists before mounting
    assets_dir = frontend_build_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Health check for the combined service (must be defined before mounting backend)
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ontario-tax-app-combined"}

@app.get("/")
async def root():
    """Serve the frontend index.html for the root route"""
    index_path = frontend_build_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Ontario Tax App", "frontend_dir": str(frontend_build_dir)}

# Include all routes from the backend app directly into the main app
# This avoids mounting issues and ensures proper route precedence
app.include_router(backend_app.router)

# Serve the frontend for all other routes (must be last due to catch-all)
if frontend_build_dir.exists():
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the frontend SPA for all non-API routes"""
        # Skip API routes - they should be handled by the backend app
        if full_path.startswith("api/"):
            return {"error": "API route not found"}
        
        # Check if it's a specific file request
        file_path = frontend_build_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        # For all other routes, serve index.html (SPA routing)
        index_path = frontend_build_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        
        # Fallback
        return {"error": "Frontend not found", "path": str(frontend_build_dir)}
else:
    # If no frontend directory exists, create a simple fallback
    @app.get("/{full_path:path}")
    async def serve_fallback(full_path: str):
        """Fallback when frontend is not available"""
        return {"message": "Frontend not available", "api_docs": "/api/v1/docs"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
