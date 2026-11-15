"""
FastAPI application entry point for PARALLAX.
Provides unified entry point for Vercel deployment and local execution.
"""
import sys
from pathlib import Path

# Add backend directory and parent directory to sys.path so 'app' and 'backend' imports resolve
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
for directory in [str(CURRENT_DIR), str(PARENT_DIR)]:
    if directory not in sys.path:
        sys.path.insert(0, directory)

from app.main import app

# Include analysis pipeline route if service module is available
try:
    from backend.service import analyze_flood_event
    app.add_api_route("/api/v1/analyze", analyze_flood_event, methods=["POST"], tags=["Pipeline"])
except Exception:
    try:
        from service import analyze_flood_event
        app.add_api_route("/api/v1/analyze", analyze_flood_event, methods=["POST"], tags=["Pipeline"])
    except Exception:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
