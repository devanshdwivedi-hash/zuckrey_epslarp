import uvicorn
import logging
from fastapi import Response
from fastapi.responses import HTMLResponse

from config.settings import settings
from config.persona_config import PERSONA_NAME, PERSONA_SYSTEM_PROMPT
from src.api.main import app
from src.api.routes import router as api_router

# Configure standard logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("autonomous_agent")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.get("/", response_class=HTMLResponse)
async def root_dashboard():
    """
    Renders a stunning dashboard outlining the state of the system and active persona configuration.
    """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Autonomous AI Agent Bunker</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-primary: #0a0c10;
                --bg-secondary: #121620;
                --accent-primary: #00ff88;
                --accent-secondary: #00e1ff;
                --text-main: #f0f3f8;
                --text-muted: #8b9bb4;
                --border-color: #242c3d;
                --glow-color: rgba(0, 255, 136, 0.15);
            }}

            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}

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

            .logo-area {{
                display: flex;
                align-items: center;
                gap: 1rem;
            }}

            .avatar-glow {{
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                box-shadow: 0 0 15px var(--accent-primary);
                position: relative;
                animation: pulse 3s infinite ease-in-out;
            }}

            @keyframes pulse {{
                0% {{ transform: scale(1); box-shadow: 0 0 15px var(--accent-primary); }}
                50% {{ transform: scale(1.05); box-shadow: 0 0 25px var(--accent-secondary); }}
                100% {{ transform: scale(1); box-shadow: 0 0 15px var(--accent-primary); }}
            }}

            h1 {{
                font-size: 1.8rem;
                font-weight: 800;
                background: linear-gradient(to right, #ffffff, var(--text-muted));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}

            .status-badge {{
                background: rgba(0, 255, 136, 0.1);
                border: 1px solid var(--accent-primary);
                color: var(--accent-primary);
                padding: 0.35rem 0.85rem;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}

            .status-dot {{
                width: 8px;
                height: 8px;
                background-color: var(--accent-primary);
                border-radius: 50%;
                animation: blink 1.5s infinite;
            }}

            @keyframes blink {{
                0%, 100% {{ opacity: 0.4; }}
                50% {{ opacity: 1; }}
            }}

            .grid-container {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 2rem;
                flex-grow: 1;
            }}

            @media(max-width: 900px) {{
                .grid-container {{
                    grid-template-columns: 1fr;
                }}
            }}

            .card {{
                background-color: var(--bg-secondary);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 2rem;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
                position: relative;
                overflow: hidden;
            }}

            .card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: linear-gradient(to right, var(--accent-primary), var(--accent-secondary));
            }}

            .card-title {{
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 1.2rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: #fff;
            }}

            .code-block {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.85rem;
                background-color: #080a0e;
                padding: 1rem;
                border-radius: 6px;
                border: 1px solid #1c2331;
                overflow-x: auto;
                color: #a5b4fc;
                white-space: pre-wrap;
                max-height: 320px;
            }}

            .metadata-list {{
                list-style: none;
            }}

            .metadata-item {{
                display: flex;
                justify-content: space-between;
                padding: 0.75rem 0;
                border-bottom: 1px solid var(--border-color);
            }}

            .metadata-item:last-child {{
                border-bottom: none;
            }}

            .metadata-label {{
                color: var(--text-muted);
                font-weight: 400;
            }}

            .metadata-value {{
                font-family: 'JetBrains Mono', monospace;
                color: var(--accent-secondary);
                font-size: 0.9rem;
            }}

            .module-list {{
                margin-top: 1rem;
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
                gap: 0.75rem;
            }}

            .module-tag {{
                background: #192030;
                border: 1px solid var(--border-color);
                padding: 0.5rem;
                text-align: center;
                border-radius: 6px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
                transition: all 0.3s ease;
            }}

            .module-tag:hover {{
                border-color: var(--accent-secondary);
                background: #1e293b;
                transform: translateY(-2px);
            }}

            footer {{
                text-align: center;
                margin-top: 3rem;
                color: var(--text-muted);
                font-size: 0.85rem;
                border-top: 1px solid var(--border-color);
                padding-top: 1.5rem;
            }}
        </style>
    </head>
    <body>
        <header>
            <div class="logo-area">
                <div class="avatar-glow"></div>
                <div>
                    <h1>Zuckrey EpsLarp Bunker API</h1>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">Autonomous Pipeline & Feed API</p>
                </div>
            </div>
            <div class="status-badge">
                <div class="status-dot"></div>
                System Active
            </div>
        </header>

        <div class="grid-container">
            <!-- Active LLM Persona -->
            <div class="card">
                <div class="card-title">
                    <span style="color: var(--accent-primary);">🕵️‍♂️</span> Active LLM Persona
                </div>
                <div class="metadata-item" style="margin-bottom: 1rem;">
                    <span class="metadata-label">Persona Name:</span>
                    <span class="metadata-value" style="color: var(--accent-primary);">{PERSONA_NAME}</span>
                </div>
                <div class="code-block" style="font-size: 0.8rem; line-height: 1.4;">{PERSONA_SYSTEM_PROMPT}</div>
            </div>

            <!-- Configuration & API Endpoints -->
            <div class="card" style="display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div class="card-title">
                        <span style="color: var(--accent-secondary);">📡</span> Active Endpoints & Settings
                    </div>
                    <ul class="metadata-list">
                        <li class="metadata-item">
                            <span class="metadata-label">Feed API:</span>
                            <span class="metadata-value"><a href="/feed" style="color: var(--accent-primary);">GET /feed</a></span>
                        </li>
                        <li class="metadata-item">
                            <span class="metadata-label">OpenAPI Specs:</span>
                            <span class="metadata-value"><a href="/docs" style="color: var(--accent-secondary);">GET /docs</a></span>
                        </li>
                        <li class="metadata-item">
                            <span class="metadata-label">Embedding Model:</span>
                            <span class="metadata-value">{settings.EMBEDDING_MODEL}</span>
                        </li>
                        <li class="metadata-item">
                            <span class="metadata-label">Database Connection:</span>
                            <span class="metadata-value">{settings.DATABASE_URL.split('///')[0]}///...</span>
                        </li>
                    </ul>
                </div>

                <div style="margin-top: 2rem;">
                    <div class="card-title" style="font-size: 1.1rem; margin-bottom: 0.5rem;">
                        Monorepo Component Map
                    </div>
                    <div class="module-list">
                        <div class="module-tag">config/</div>
                        <div class="module-tag">scrapers/</div>
                        <div class="module-tag">intelligence/</div>
                        <div class="module-tag">memory/</div>
                        <div class="module-tag">db/</div>
                        <div class="module-tag">scheduler/</div>
                        <div class="module-tag">api/</div>
                    </div>
                </div>
            </div>
        </div>

        <footer>
            Autonomous AI Content Agent &copy; {settings.PORT} server running in {"Debug Mode" if settings.DEBUG else "Production Mode"}
        </footer>
    </body>
    </html>
    """
    return html_content


if __name__ == "__main__":
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
