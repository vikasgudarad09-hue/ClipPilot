"""
OmniPost Studio - Main Application Server & Desktop Launcher
Runs the local REST API and launches the modern desktop UI.
"""
import os
import sys
import json
import time
import threading
import webbrowser
from typing import Dict, Any, List, Optional

if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    APP_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = BASE_DIR

os.chdir(APP_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.scheduler import CadenceScheduler
from core.ai_metadata import AIMetadataGenerator
from core.folder_watcher import FolderWatcher
from core.publishers import get_all_publishers
from core.license_manager import LicenseManager

app = FastAPI(title="ClipPilot", version="1.0.0")

# Security Hardening: Restrict CORS strictly to local loopback origins to prevent cross-site port scanning & CSRF
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8765",
        "http://localhost:8765"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

ALLOWED_VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}
ALLOWED_PREVIEW_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

# Mount static files and set up data directory
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(APP_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

ACCOUNTS_CONFIG_PATH = os.path.join(DATA_DIR, "accounts.json")

# Initialize modules
scheduler = CadenceScheduler(os.path.join(DATA_DIR, "queue.json"))
ai_generator = AIMetadataGenerator()
publishers = get_all_publishers(DATA_DIR)
license_mgr = LicenseManager(DATA_DIR)

# Load saved platform configs
def load_accounts_config():
    if os.path.exists(ACCOUNTS_CONFIG_PATH):
        try:
            with open(ACCOUNTS_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for pid, cfg in data.items():
                    if pid in publishers:
                        publishers[pid].set_config(cfg)
        except Exception as e:
            print(f"Error loading accounts config: {e}")

load_accounts_config()

# Global upload state
upload_state = {
    "is_uploading": False,
    "current_item_id": None,
    "progress": 0,
    "status_message": "Idle",
    "completed_count": 0,
    "total_count": 0
}

# --- Pydantic Request Models ---
class AddVideoRequest(BaseModel):
    file_path: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    thumbnail_path: Optional[str] = None
    target_platforms: Optional[List[str]] = None

class CadenceRequest(BaseModel):
    frequency_per_week: int = 3
    active_days: Optional[List[str]] = None
    preferred_time: str = "18:00"
    start_date: Optional[str] = None
    jitter_minutes: int = 0

class UpdateItemRequest(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    thumbnail_path: Optional[str] = None
    target_platforms: Optional[List[str]] = None
    scheduled_time_iso: Optional[str] = None
    scheduled_time_human: Optional[str] = None

class AIGenerateRequest(BaseModel):
    topic: str
    language: str = "hinglish"
    category: str = "educational"

class PlatformConfigRequest(BaseModel):
    platform_id: str
    config: Dict[str, Any]

class StartUploadRequest(BaseModel):
    item_ids: Optional[List[str]] = None

class ActivateLicenseRequest(BaseModel):
    key: str


# --- API Routes ---

@app.get("/api/license/status")
def get_license_status():
    return license_mgr.get_status()

@app.post("/api/license/activate")
def activate_license(req: ActivateLicenseRequest):
    success, msg = license_mgr.activate(req.key)
    return {"success": success, "message": msg, "status": license_mgr.get_status()}

@app.get("/api/queue")
def get_queue():
    return {"queue": scheduler.queue}

@app.post("/api/queue/add")
def add_to_queue(req: AddVideoRequest):
    try:
        clean_path = os.path.realpath(req.file_path)
        ext = os.path.splitext(clean_path)[1].lower()
        if ext not in ALLOWED_VIDEO_EXTS:
            raise HTTPException(status_code=400, detail="Invalid video format. Supported: MP4, MOV, MKV, AVI, WEBM")
        if not (os.path.exists(clean_path) and os.path.isfile(clean_path)):
            raise HTTPException(status_code=400, detail="Video file does not exist on disk")

        item = scheduler.add_video(
            file_path=clean_path,
            title=req.title,
            description=req.description or "",
            tags=req.tags,
            thumbnail_path=req.thumbnail_path,
            target_platforms=req.target_platforms
        )
        return {"success": True, "item": item}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/queue/remove")
def remove_from_queue(req: Dict[str, str]):
    item_id = req.get("id")
    if not item_id:
        raise HTTPException(status_code=400, detail="Missing id")
    success = scheduler.remove_video(item_id)
    return {"success": success}

@app.post("/api/queue/clear")
def clear_queue():
    scheduler.clear_queue()
    return {"success": True}

@app.post("/api/queue/update")
def update_item(req: UpdateItemRequest):
    updates = req.dict(exclude_unset=True)
    item_id = updates.pop("id")
    updated = scheduler.update_item(item_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"success": True, "item": updated}

@app.post("/api/cadence/preview")
def preview_cadence(req: CadenceRequest):
    item_count = len([x for x in scheduler.queue if x.get("status") in ["queued", "scheduled"]])
    count = max(item_count, 5)
    slots = scheduler.calculate_schedule_slots(
        count=count,
        frequency_per_week=req.frequency_per_week,
        active_days=req.active_days,
        preferred_time=req.preferred_time,
        start_date=req.start_date,
        jitter_minutes=req.jitter_minutes
    )
    return {"slots": slots}

@app.post("/api/cadence/apply")
def apply_cadence(req: CadenceRequest):
    slots = scheduler.apply_cadence_to_queue(
        frequency_per_week=req.frequency_per_week,
        active_days=req.active_days,
        preferred_time=req.preferred_time,
        start_date=req.start_date
    )
    return {"success": True, "slots": slots, "queue": scheduler.queue}

@app.post("/api/ai/generate")
def generate_ai_metadata(req: AIGenerateRequest):
    metadata = ai_generator.generate(
        topic_or_title=req.topic,
        language=req.language,
        category=req.category
    )
    return {"metadata": metadata}

@app.get("/api/platforms")
def get_platforms():
    res = []
    for pid, pub in publishers.items():
        val = pub.validate_credentials()
        res.append({
            "id": pid,
            "name": pub.display_name,
            "is_configured": pub.is_configured(),
            "status": val
        })
    return {"platforms": res}

@app.post("/api/platforms/configure")
def configure_platform(req: PlatformConfigRequest):
    pid = req.platform_id
    if pid not in publishers:
        raise HTTPException(status_code=404, detail="Unknown platform")
    publishers[pid].set_config(req.config)
    
    # Save to accounts.json
    all_configs = {}
    if os.path.exists(ACCOUNTS_CONFIG_PATH):
        try:
            with open(ACCOUNTS_CONFIG_PATH, "r", encoding="utf-8") as f:
                all_configs = json.load(f)
        except Exception:
            pass
    all_configs[pid] = req.config
    with open(ACCOUNTS_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(all_configs, f, indent=2)

    val = publishers[pid].validate_credentials()
    return {"success": True, "status": val}

@app.post("/api/youtube/login")
def youtube_login():
    """Trigger 1-click Google OAuth browser login."""
    yt_pub = publishers.get("youtube")
    if not yt_pub:
        raise HTTPException(status_code=404, detail="YouTube publisher not found")
    res = yt_pub.authenticate_interactive()
    return res

@app.get("/api/browse/video")
def browse_video():
    """Opens native Windows file dialog to pick video file."""
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    file_path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=[("Video Files", "*.mp4 *.mov *.mkv *.avi *.webm"), ("All Files", "*.*")]
    )
    root.destroy()
    return {"file_path": file_path or ""}

@app.get("/api/browse/thumbnail")
def browse_thumbnail():
    """Opens native Windows file dialog to pick thumbnail."""
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    file_path = filedialog.askopenfilename(
        title="Select Thumbnail Image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp"), ("All Files", "*.*")]
    )
    root.destroy()
    return {"file_path": file_path or ""}

@app.get("/api/browse/image_preview")
def image_preview(path: str):
    """Safely serves local image preview for thumbnails with path traversal protection."""
    clean_path = os.path.realpath(path)
    ext = os.path.splitext(clean_path)[1].lower()
    if ext not in ALLOWED_PREVIEW_EXTS:
        raise HTTPException(status_code=403, detail="Forbidden: Only image preview files allowed")
    if os.path.exists(clean_path) and os.path.isfile(clean_path):
        return FileResponse(clean_path)
    raise HTTPException(status_code=404, detail="Image not found")

@app.get("/api/browse/video_stream")
def video_stream(path: str):
    """Safely streams local video file for in-app video playback."""
    clean_path = os.path.realpath(path)
    ext = os.path.splitext(clean_path)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTS:
        raise HTTPException(status_code=403, detail="Forbidden: Only video files can be previewed")
    if os.path.exists(clean_path) and os.path.isfile(clean_path):
        return FileResponse(clean_path, media_type="video/mp4")
    raise HTTPException(status_code=404, detail="Video file not found")

@app.get("/api/upload/status")
def get_upload_status():
    return upload_state

def _run_upload_pipeline(item_ids: Optional[List[str]] = None):
    global upload_state
    items_to_upload = []
    if item_ids:
        items_to_upload = [x for x in scheduler.queue if x["id"] in item_ids]
    else:
        items_to_upload = [x for x in scheduler.queue if x.get("status") in ["queued", "scheduled"]]

    upload_state["is_uploading"] = True
    upload_state["total_count"] = len(items_to_upload)
    upload_state["completed_count"] = 0

    for item in items_to_upload:
        item_id = item["id"]
        upload_state["current_item_id"] = item_id
        upload_state["status_message"] = f"Processing {item['title']}..."
        scheduler.update_item(item_id, {"status": "uploading", "upload_progress": 0})

        target_platforms = item.get("target_platforms") or ["youtube"]
        all_success = True
        urls = {}

        def make_progress_cb(item_idx):
            def cb(pct, msg):
                upload_state["progress"] = pct
                upload_state["status_message"] = msg
                scheduler.update_item(item_idx, {"upload_progress": pct})
            return cb

        for platform_id in target_platforms:
            pub = publishers.get(platform_id)
            if not pub:
                continue

            upload_state["status_message"] = f"Pushing to {pub.display_name}..."
            res = pub.upload_video(
                file_path=item["file_path"],
                title=item["title"],
                description=item["description"],
                tags=item["tags"],
                schedule_time_iso=item.get("scheduled_time_iso"),
                thumbnail_path=item.get("thumbnail_path"),
                progress_callback=make_progress_cb(item_id)
            )

            if res.get("success"):
                urls[platform_id] = res.get("url", "Scheduled")
            else:
                all_success = False
                scheduler.update_item(item_id, {
                    "status": "error",
                    "error_message": f"{pub.display_name}: {res.get('error')}"
                })
                break

        if all_success:
            scheduler.update_item(item_id, {
                "status": "published" if not item.get("scheduled_time_iso") else "scheduled",
                "upload_progress": 100,
                "published_urls": urls
            })
            upload_state["completed_count"] += 1
            license_mgr.increment_published_count(1)

        time.sleep(1)

    upload_state["is_uploading"] = False
    upload_state["status_message"] = "Completed all uploads."
    upload_state["progress"] = 100

@app.post("/api/upload/start")
def start_upload(req: StartUploadRequest, background_tasks: BackgroundTasks):
    global upload_state
    if upload_state["is_uploading"]:
        return {"success": False, "message": "An upload task is already in progress."}

    if req.item_ids:
        items_to_upload = [x for x in scheduler.queue if x["id"] in req.item_ids]
    else:
        items_to_upload = [x for x in scheduler.queue if x.get("status") in ["queued", "scheduled"]]

    if not items_to_upload:
        return {"success": False, "message": "Your queue is empty or no videos are ready to publish."}

    allowed, limit_msg = license_mgr.can_publish_batch(len(items_to_upload))
    if not allowed:
        return {
            "success": False,
            "requires_pro": True,
            "message": limit_msg,
            "status": license_mgr.get_status()
        }

    background_tasks.add_task(_run_upload_pipeline, req.item_ids)
    return {"success": True, "message": "Bulk upload pipeline started in background."}

# Serve Frontend
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


def start_server_and_gui():
    import uvicorn
    server_thread = threading.Thread(
        target=lambda: uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning"),
        daemon=True
    )
    server_thread.start()
    time.sleep(1.2)

    url = "http://127.0.0.1:8765"
    print(f"=======================================================")
    print(f"✈️  ClipPilot is running at: {url}")
    print(f"    Put Your Video Publishing on Autopilot")
    print(f"=======================================================")

    # Try launching modern native pywebview desktop window
    try:
        import webview
        webview.create_window(
            title="ClipPilot | Video Publishing on Autopilot",
            url=url,
            width=1280,
            height=860,
            min_size=(960, 680),
            background_color="#0d1117"
        )
        webview.start()
    except Exception as e:
        print(f"Native desktop window opened in default browser ({e})")
        webbrowser.open(url)
        # Keep alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down ClipPilot.")

if __name__ == "__main__":
    start_server_and_gui()
