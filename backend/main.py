import os
import secrets
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from services.hotkey_mgr import hotkey_mgr
from services.case_mgr import case_manager

app = FastAPI(title="Messenger Mode v0.2")

CASE_ROOT = Path(os.path.expanduser("~/MessengerCases")).resolve()
ALLOWED_ORIGINS = {
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
}
ALLOWED_HOSTS = {
    "127.0.0.1:8000",
    "localhost:8000",
    "[::1]:8000",
}
CSRF_TOKEN = secrets.token_urlsafe(32)

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(ALLOWED_ORIGINS),
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "X-InterAI-CSRF"],
)


def _error(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


@app.middleware("http")
async def protect_local_api(request: Request, call_next):
    """Reject requests that did not come through the expected loopback UI.

    CORS controls response visibility in browsers; it is not treated as an
    authorization mechanism.  Host, Origin and a per-process CSRF token are
    checked independently for API access.
    """
    host = (request.headers.get("host") or "").lower()
    if host not in ALLOWED_HOSTS:
        return _error(403, "Host is not an allowed local endpoint")

    origin = request.headers.get("origin")
    if origin is not None and origin not in ALLOWED_ORIGINS:
        return _error(403, "Origin is not allowed")

    path = request.url.path
    if path.startswith("/api/") and path not in {"/api/health", "/api/session"}:
        if origin not in ALLOWED_ORIGINS:
            return _error(403, "Origin is required for API access")

        supplied = request.headers.get("x-interai-csrf", "")
        if not supplied or not secrets.compare_digest(supplied, CSRF_TOKEN):
            return _error(403, "Missing or invalid CSRF token")

    return await call_next(request)


def _validate_case_name(case_name: str) -> Path:
    if (
        not case_name
        or case_name in {".", ".."}
        or "/" in case_name
        or "\\" in case_name
        or Path(case_name).name != case_name
    ):
        raise HTTPException(status_code=400, detail="Invalid case name")

    candidate = (CASE_ROOT / case_name).resolve()
    try:
        candidate.relative_to(CASE_ROOT)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Case path escapes case root") from exc

    if not candidate.is_dir():
        raise HTTPException(status_code=404, detail="Case not found")
    return candidate


def _case_subdir(case_name: str, subdir: str) -> Path:
    allowed = {"case": "", "input": "input", "output": "output", "handoff": "handoff"}
    if subdir not in allowed:
        raise HTTPException(status_code=400, detail="Folder is not an allowed case directory")

    case_dir = _validate_case_name(case_name)
    candidate = (case_dir / allowed[subdir]).resolve()
    try:
        candidate.relative_to(case_dir)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Folder escapes case directory") from exc

    if not candidate.is_dir():
        raise HTTPException(status_code=404, detail="Folder not found")
    return candidate


def _latest_screenshot(case_dir: Path) -> Path | None:
    input_dir = case_dir / "input"
    if not input_dir.is_dir():
        return None
    screenshots = sorted(
        (p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == ".png"),
        key=lambda p: p.name,
        reverse=True,
    )
    return screenshots[0] if screenshots else None


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/session")
def local_session():
    # A cross-origin browser request is rejected by the middleware before it can
    # read this token.  The token is intentionally ephemeral and changes at
    # every backend start.
    return {"csrf_token": CSRF_TOKEN}


@app.get("/api/cases")
def list_cases():
    # Do not expose absolute local filesystem paths to the browser.
    return [{"name": c.name, "created_at": c.created_at} for c in case_manager.list_cases()]


@app.get("/api/case/{case_name}/assets")
def get_case_assets(case_name: str):
    case_dir = _validate_case_name(case_name)
    input_dir = case_dir / "input"
    handoff_path = case_dir / "handoff" / "handoff.md"
    clip_path = input_dir / "clip.txt"

    handoff_content = handoff_path.read_text(encoding="utf-8") if handoff_path.is_file() else ""
    clip_content = clip_path.read_text(encoding="utf-8") if clip_path.is_file() else ""

    return {
        "has_screenshot": _latest_screenshot(case_dir) is not None,
        "handoff_content": handoff_content,
        "clip_content": clip_content,
    }


@app.get("/api/case/{case_name}/screenshot")
def get_case_screenshot(case_name: str):
    case_dir = _validate_case_name(case_name)
    screenshot = _latest_screenshot(case_dir)
    if screenshot is None:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return FileResponse(screenshot, media_type="image/png", filename=screenshot.name)


@app.post("/api/cases/{case_name}/open-folder")
def open_case_folder(case_name: str, subdir: str = "input"):
    folder = _case_subdir(case_name, subdir)
    if not hasattr(os, "startfile"):
        raise HTTPException(status_code=501, detail="Opening folders is only supported on Windows")
    os.startfile(str(folder))
    return {"status": "opened"}


@app.delete("/api/cases/{case_name}")
def delete_case(case_name: str):
    import shutil

    case_path = _validate_case_name(case_name)
    try:
        def on_rm_error(func, path, exc_info):
            import stat
            os.chmod(path, stat.S_IWRITE)
            func(path)

        shutil.rmtree(case_path, onerror=on_rm_error)
        return {"status": "deleted"}
    except Exception as exc:
        print(f"Delete failed: {exc}")
        raise HTTPException(status_code=500, detail="Delete failed") from exc


@app.post("/api/debug/trigger")
def debug_trigger():
    print("DEBUG: Triggering screenshot via HTTP")
    hotkey_mgr.on_screenshot()
    hotkey_mgr.on_clip_save()
    return {"status": "triggered"}


@app.post("/api/debug/handoff")
def debug_handoff():
    print("DEBUG: Triggering handoff via HTTP")
    hotkey_mgr.on_handoff()
    return {"status": "handoff_generated"}


frontend_path = Path(__file__).resolve().parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")


@app.on_event("startup")
def startup_event():
    print("Starting Messenger Mode Backend...")
    hotkey_mgr.start_listener()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
