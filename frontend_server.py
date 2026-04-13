import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="AI Food OS Frontend Server")

# Get the absolute path to the frontend directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Serve static files from the frontend directory
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "landing.html"))

@app.get("/{path:path}")
async def catch_all(path: str):
    file_path = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    # Default to landing.html for spa-like behavior if needed, 
    # but for now just serve if exists
    return FileResponse(os.path.join(FRONTEND_DIR, "landing.html"))

def run_frontend():
    print(f"🚀 Starting [FRONTEND] Server on http://localhost:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="error")

if __name__ == "__main__":
    run_frontend()
