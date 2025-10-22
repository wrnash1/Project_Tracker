from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from api.projects import router as projects_router
from api.reports import router as reports_router
from api.gantt import router as gantt_router
from api.tasks import router as tasks_router
from api.notes import router as notes_router
from api.ml import router as ml_router
from api.tts import router as tts_router

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="PM Project Tracker API",
        description="Verizon PM Project Tracker - PyWebView Desktop Edition",
        version="1.0.0"
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static files
    static_path = Path(__file__).parent.parent / "web_app" / "static"
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

    # Register routers
    app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
    app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
    app.include_router(gantt_router, prefix="/api/gantt", tags=["gantt"])
    app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
    app.include_router(notes_router, prefix="/api/notes", tags=["notes"])
    app.include_router(ml_router, prefix="/api/ml", tags=["ml"])
    app.include_router(tts_router, prefix="/api/tts", tags=["tts"])

    # Templates
    templates_path = Path(__file__).parent.parent / "web_app" / "templates"
    templates = Jinja2Templates(directory=str(templates_path))

    @app.get("/")
    async def root():
        """Serve main application page"""
        from fastapi.responses import HTMLResponse
        with open(templates_path / "index.html", "r") as f:
            return HTMLResponse(content=f.read())

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "version": "1.0.0"}

    return app
