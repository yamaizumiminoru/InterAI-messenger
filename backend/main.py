
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from services.hotkey_mgr import hotkey_mgr
from services.case_mgr import case_manager
import os

app = FastAPI(title="Messenger Mode MVP")

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routes ---


from fastapi.responses import FileResponse

# Config
CASE_ROOT = os.path.expanduser("~/MessengerCases")

# Mount Case Files for Frontend Access
if os.path.exists(CASE_ROOT):
    app.mount("/cases", StaticFiles(directory=CASE_ROOT), name="cases")
 
@app.get("/api/cases")
def list_cases():
    cases = case_manager.list_cases()
    # Enrich with asset URLs for frontend convenience
    # (In a real app, use a serializer, but here we just pass data)
    return cases

@app.get("/api/case/{case_name}/assets")
def get_case_assets(case_name: str):
    # Helper to find exact filenames since they have timestamps
    # This helps app.js which guessed names.
    case_path = os.path.join(CASE_ROOT, case_name)
    input_dir = os.path.join(case_path, "input")
    handoff_path = os.path.join(case_path, "handoff", "handoff.md")
    clip_path = os.path.join(input_dir, "clip.txt")
    
    screenshot = None
    if os.path.exists(input_dir):
        files = [f for f in os.listdir(input_dir) if f.endswith(".png")]
        if files:
            files.sort(reverse=True)
            screenshot = f"/cases/{case_name}/input/{files[0]}"
            
    handoff_content = ""
    if os.path.exists(handoff_path):
        with open(handoff_path, "r", encoding="utf-8") as f: handoff_content = f.read()

    clip_content = ""
    if os.path.exists(clip_path):
        with open(clip_path, "r", encoding="utf-8") as f: clip_content = f.read()

    return {
        "screenshot_url": screenshot,
        "handoff_content": handoff_content,
        "clip_content": clip_content
    }

@app.get("/api/open_folder")
def open_folder(path: str):
    if os.path.exists(path):
        os.startfile(path)
        return {"status": "opened"}
    raise HTTPException(status_code=404, detail="Path not found")

import shutil

@app.delete("/api/cases/{case_name}")
def delete_case(case_name: str):
    # Security: Ensure case_name is simple and doesn't contain path separators to prevent traversal
    if ".." in case_name or "/" in case_name or "\\" in case_name:
         raise HTTPException(status_code=400, detail="Invalid case name")

    case_path = os.path.join(CASE_ROOT, case_name)
    if os.path.exists(case_path):
        try:
            # On Windows, sometimes files are read-only or locked. 
            # A simple rmtree might fail.
            def on_rm_error(func, path, exc_info):
                import stat
                # Attempt to make writeable and try again
                os.chmod(path, stat.S_IWRITE)
                func(path)
                
            shutil.rmtree(case_path, onerror=on_rm_error)
            return {"status": "deleted"}
        except Exception as e:
            print(f"Delete failed: {e}") # Log to terminal
            raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
    raise HTTPException(status_code=404, detail="Case not found")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# Mount Frontend (assuming dist or similar, for now just static)
# We will create a simple index.html soon.
frontend_path = os.path.abspath("../frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

@app.on_event("startup")
def startup_event():
    print("Starting Messenger Mode Backend...")
    hotkey_mgr.start_listener()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
