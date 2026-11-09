"""
Facebook Publisher Module
Supports publishing videos and Reels to Facebook Pages and Groups
via Meta Graph API.
"""
import os
import time
import requests
from typing import Dict, Any, Optional, Callable
from .base import BasePublisher

class FacebookPublisher(BasePublisher):
    GRAPH_API_VERSION = "v19.0"
    BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

    def __init__(self, page_access_token: str = "", page_id: str = ""):
        super().__init__("facebook", "Facebook (Page & Reels)", "facebook")
        self.page_access_token = page_access_token
        self.page_id = page_id

    def set_config(self, config: Dict[str, Any]):
        super().set_config(config)
        self.page_access_token = config.get("page_access_token", self.page_access_token)
        self.page_id = config.get("page_id", self.page_id)

    def is_configured(self) -> bool:
        return bool(self.page_access_token and self.page_id)

    def validate_credentials(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {"valid": False, "message": "Facebook Page Token or Page ID missing."}
        try:
            url = f"{self.BASE_URL}/{self.page_id}"
            params = {"fields": "id,name,fan_count,link", "access_token": self.page_access_token}
            res = requests.get(url, params=params, timeout=10)
            data = res.json()
            if "error" in data:
                return {"valid": False, "message": data["error"].get("message")}
            return {
                "valid": True,
                "name": data.get("name"),
                "fan_count": data.get("fan_count"),
                "message": f"Connected to Facebook Page: {data.get('name')}"
            }
        except Exception as e:
            return {"valid": False, "message": str(e)}

    def upload_video(
        self,
        file_path: str,
        title: str,
        description: str,
        tags: list,
        schedule_time_iso: Optional[str] = None,
        thumbnail_path: Optional[str] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        extra_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}

        if not self.is_configured():
            if progress_callback:
                for pct in range(20, 101, 30):
                    progress_callback(pct, f"Preparing Facebook Post ({pct}%)...")
                    time.sleep(0.2)
            return {
                "success": True,
                "post_id": f"fb_sim_{int(time.time())}",
                "url": "https://facebook.com/simulated_post",
                "scheduled": bool(schedule_time_iso),
                "scheduled_for": schedule_time_iso,
                "is_simulation": True,
                "message": "Staged in simulation mode. Connect Facebook Page Token for live broadcast."
            }

        try:
            # Facebook Graph API video upload endpoint
            upload_url = f"{self.BASE_URL}/{self.page_id}/videos"
            payload = {
                "title": title[:255],
                "description": f"{title}\n\n{description}",
                "access_token": self.page_access_token
            }
            if schedule_time_iso:
                import datetime
                dt = datetime.datetime.fromisoformat(schedule_time_iso.replace("Z", "+00:00"))
                payload["scheduled_publish_time"] = int(dt.timestamp())
                payload["published"] = False

            if progress_callback:
                progress_callback(30, "Uploading video to Facebook...")

            with open(file_path, "rb") as video_file:
                files = {"source": video_file}
                res = requests.post(upload_url, data=payload, files=files, timeout=120)
                res_data = res.json()

            if "error" in res_data:
                return {"success": False, "error": res_data["error"].get("message")}

            video_id = res_data.get("id")
            if progress_callback:
                progress_callback(100, "Done!")

            return {
                "success": True,
                "post_id": video_id,
                "url": f"https://facebook.com/{video_id}",
                "scheduled": bool(schedule_time_iso),
                "scheduled_for": schedule_time_iso,
                "is_simulation": False
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
