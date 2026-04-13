"""
AI Smart Food OS — FastAPI Application
Premium dark intelligence platform: think, eat, thrive.
Pure REST API backend.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

# Lazy-import routers to avoid circular deps
from routes.api_v2 import router as api_router

app = FastAPI(
    title="AI Smart Food OS API",
    description="AI-powered food intelligence: What, Why & How Much to eat.",
    version="2.0.0"
)

# ── Middleware ──
app.add_middleware(GZipMiddleware, minimum_size=500)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://localhost:8000", "http://127.0.0.1:5000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register API router ──
app.include_router(api_router)

# Try to include auth router if it exists
try:
    from routes.auth_v2 import router as auth_router
    app.include_router(auth_router)
except ImportError:
    pass  # Auth routes are embedded in api_v2


# ── System Health check ──
@app.get("/api/status")
async def api_status():
    return {"status": "ok", "version": "2.0.0", "platform": "AI Smart Food OS API"}


def run_backend():
    print(f"📡 Starting [BACKEND] Server on http://localhost:8000")
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    from multiprocessing import Process
    from frontend_server import run_frontend
    
    # Start Backend and Frontend as separate processes
    backend_proc = Process(target=run_backend)
    frontend_proc = Process(target=run_frontend)
    
    backend_proc.start()
    frontend_proc.start()
    
    try:
        backend_proc.join()
        frontend_proc.join()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
