import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

# Fix Vercel Serverless Function module resolution
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from config.persona_config import PERSONA_NAME, PERSONA_SYSTEM_PROMPT
from src.db.database import init_db
from src.api.routes import router as api_router

logger = logging.getLogger("autonomous_agent.api")

is_vercel = "VERCEL" in os.environ


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.
    Safely initializes DB schema tables on boot.
    Only starts APScheduler background thread when running locally (not on Vercel serverless).
    """
    logger.info("Initializing database schema on startup...")
    try:
        init_db()
    except Exception as db_err:
        logger.error(f"Handled database initialization notice on app startup: {db_err}")
    
    if not is_vercel:
        try:
            from src.scheduler.cron import start_scheduler
            logger.info("Starting background scheduler for local runtime...")
            start_scheduler(run_immediately=False)
        except Exception as sched_err:
            logger.warning(f"Could not start local background scheduler: {sched_err}")
    else:
        logger.info("Vercel Serverless Mode detected. Background thread scheduler disabled (using /api/cron).")
    
    yield
    
    if not is_vercel:
        try:
            from src.scheduler.cron import stop_scheduler
            logger.info("Shutting down background scheduler...")
            stop_scheduler()
        except Exception:
            pass


app = FastAPI(
    title="Autonomous Content Agent API",
    description="REST API serving accumulated technical security post feed to evaluators.",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Configure CORSMiddleware with wildcard permissions as required
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend & assets static directory if present
frontend_dir = root_dir / "frontend"
if frontend_dir.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_dir)), name="frontend")

assets_dir = root_dir / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.get("/favicon.png", include_in_schema=False)
async def favicon_png():
    return Response(status_code=204)


@app.get("/", response_class=HTMLResponse)
async def root_dashboard():
    """
    Renders the Y2K Retro OS Bunker Dashboard if frontend/index.html exists,
    or falls back to the embedded status dashboard template.
    """
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))

    try:
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Autonomous AI Agent Bunker</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
            <style>
                :root {{
                    --bg-primary: #0a0c10;
                    --bg-secondary: #121620;
                    --accent-primary: #00ff88;
                    --accent-secondary: #00e1ff;
                    --text-main: #f0f3f8;
                    --text-muted: #8b9bb4;
                    --border-color: #242c3d;
                }}
                * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                body {{
                    background-color: var(--bg-primary);
                    color: var(--text-main);
                    font-family: 'Outfit', sans-serif;
                    line-height: 1.6;
                    padding: 2rem;
                    display: flex;
                    flex-direction: column;
                    min-height: 100vh;
                }}
                header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-bottom: 2px solid var(--border-color);
                    padding-bottom: 1.5rem;
                    margin-bottom: 2rem;
                }}
                .logo-area {{ display: flex; align-items: center; gap: 1rem; }}
                .avatar-glow {{
                    width: 50px; height: 50px; border-radius: 50%;
                    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                    box-shadow: 0 0 15px var(--accent-primary);
                }}
                h1 {{
                    font-size: 1.8rem; font-weight: 800;
                    background: linear-gradient(to right, #ffffff, var(--text-muted));
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                }}
                .status-badge {{
                    background: rgba(0, 255, 136, 0.1); border: 1px solid var(--accent-primary);
                    color: var(--accent-primary); padding: 0.35rem 0.85rem; border-radius: 20px;
                    font-size: 0.85rem; font-weight: 600; display: flex; align-items: center; gap: 0.5rem;
                }}
                .status-dot {{ width: 8px; height: 8px; background-color: var(--accent-primary); border-radius: 50%; }}
                .grid-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; flex-grow: 1; }}
                @media(max-width: 900px) {{ .grid-container {{ grid-template-columns: 1fr; }} }}
                .card {{
                    background-color: var(--bg-secondary); border: 1px solid var(--border-color);
                    border-radius: 12px; padding: 2rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
                }}
                .card-title {{ font-size: 1.25rem; font-weight: 600; margin-bottom: 1.2rem; display: flex; align-items: center; gap: 0.5rem; color: #fff; }}
                .code-block {{
                    font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; background-color: #080a0e;
                    padding: 1rem; border-radius: 6px; border: 1px solid #1c2331; overflow-x: auto; color: #a5b4fc;
                    white-space: pre-wrap; max-height: 320px;
                }}
                .metadata-list {{ list-style: none; }}
                .metadata-item {{ display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid var(--border-color); }}
                .metadata-label {{ color: var(--text-muted); font-weight: 400; }}
                .metadata-value {{ font-family: 'JetBrains Mono', monospace; color: var(--accent-secondary); font-size: 0.9rem; }}
                footer {{ text-align: center; margin-top: 3rem; color: var(--text-muted); font-size: 0.85rem; border-top: 1px solid var(--border-color); padding-top: 1.5rem; }}
            </style>
        </head>
        <body>
            <header>
                <div class="logo-area">
                    <div class="avatar-glow"></div>
                    <div>
                        <h1>Zuckrey EpsLarp Bunker API</h1>
                        <p style="color: var(--text-muted); font-size: 0.9rem;">Autonomous Pipeline & Serverless Vercel Deployment</p>
                    </div>
                </div>
                <div class="status-badge">
                    <div class="status-dot"></div> System Active
                </div>
            </header>
            <div class="grid-container">
                <div class="card">
                    <div class="card-title"><span style="color: var(--accent-primary);">🕵️‍♂️</span> Active LLM Persona</div>
                    <div class="metadata-item" style="margin-bottom: 1rem;">
                        <span class="metadata-label">Persona Name:</span>
                        <span class="metadata-value" style="color: var(--accent-primary);">{PERSONA_NAME}</span>
                    </div>
                    <div class="code-block">{PERSONA_SYSTEM_PROMPT}</div>
                </div>
                <div class="card" style="display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div class="card-title"><span style="color: var(--accent-secondary);">📡</span> Vercel Endpoints</div>
                        <ul class="metadata-list">
                            <li class="metadata-item">
                                <span class="metadata-label">Feed API:</span>
                                <span class="metadata-value"><a href="/feed" style="color: var(--accent-primary);">GET /feed</a></span>
                            </li>
                            <li class="metadata-item">
                                <span class="metadata-label">Vercel Serverless Cron:</span>
                                <span class="metadata-value"><a href="/api/cron" style="color: var(--accent-secondary);">GET /api/cron</a></span>
                            </li>
                            <li class="metadata-item">
                                <span class="metadata-label">OpenAPI Specs:</span>
                                <span class="metadata-value"><a href="/docs" style="color: var(--accent-secondary);">GET /docs</a></span>
                            </li>
                            <li class="metadata-item">
                                <span class="metadata-label">Embedding Model:</span>
                                <span class="metadata-value">{settings.EMBEDDING_MODEL}</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            <footer>Autonomous AI Content Agent Serverless Runtime</footer>
        </body>
        </html>
        """
        return html_content
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


# Include API endpoints router
app.include_router(api_router)
