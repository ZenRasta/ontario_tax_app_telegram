#!/usr/bin/env python3
"""
Combined FastAPI + Static File Server for DigitalOcean App Platform

This serves:
- FastAPI backend at /api/* routes (backend app has /api/v1 prefix internally)
- Frontend static files for all other routes
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Import the backend FastAPI app
from backend.app.main import app as backend_app

# Create the main app
app = FastAPI(title="Ontario Tax App", description="Combined Frontend + Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Health check for the combined service
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ontario-tax-app-combined"}

# Include all routes from the backend app directly into the main app
# This ensures proper route precedence and avoids mounting conflicts
from backend.app.main import router as backend_router, debug_router as backend_debug_router
app.include_router(backend_router, prefix="/api/v1")
app.include_router(backend_debug_router, prefix="/api/v1/debug")

@app.get("/")
async def root():
    """Serve the frontend index.html for the root route"""
    index_path = frontend_build_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Ontario Tax App", "frontend_dir": str(frontend_build_dir)}

# Serve the frontend for all other routes (must be last due to catch-all)
# This catch-all route should NOT match /api/* routes due to mounting above
if frontend_build_dir.exists():
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the frontend SPA for all non-API routes"""
        # This should never be reached for /api/* routes due to mounting above
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        
        # Check if it's a specific file request
        file_path = frontend_build_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        # For all other routes, serve index.html (SPA routing)
        index_path = frontend_build_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        
        # Fallback
        raise HTTPException(status_code=404, detail="Frontend file not found")
else:
    # If no frontend directory exists, create a simple fallback
    @app.get("/{full_path:path}")
    async def serve_fallback(full_path: str):
        """Fallback when frontend is not available"""
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        return {"message": "Frontend not available", "api_docs": "/api/v1/docs"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
