"""Main FastAPI application entrypoint for FixGraph."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from fixgraph.api.routes import router

app = FastAPI(
    title="FixGraph — Smart Guided Troubleshooting Engine",
    description="Samsung PRISM GenAI Hackathon 3.0 Theme 2 Execution API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

app.include_router(router)


from pathlib import Path


@app.get("/", response_class=HTMLResponse)
def root_ui():
    """Interactive visual dashboard for FixGraph troubleshooting engine."""
    template_path = Path(__file__).parent / "web" / "templates" / "index.html"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<html><body><h1>FixGraph UI</h1><p>index.html not found.</p></body></html>"
