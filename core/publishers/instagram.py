"""
Instagram Publisher Module
Supports publishing and scheduling Instagram Reels and Video Posts
via Meta Graph API (Instagram Graph API).
"""
import os
import time
import requests
from typing import Dict, Any, Optional, Callable
from .base import BasePublisher

class InstagramPublisher(BasePublisher):
    GRAPH_API_VERSION = "v19.0"
    BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

    def __init__(self, access_token: str = "", instagram_account_id: str = ""):
        super().__init__("instagram", "Instagram (Reels & Feed)", "instagram")
        self.access_token = access_token
        self.instagram_account_id = instagram_account_id

    def set_config(self, config: Dict[str, Any]):
        super().set_config(config)
        self.access_token = config.get("access_token", self.access_token)
        self.instagram_account_id = config.get("instagram_account_id", self.instagram_account_id)

    def is_configured(self) -> bool:
        return bool(self.access_token and self.instagram_account_id)

    def validate_credentials(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "valid": False,
                "message": "Instagram Access Token or Account ID missing."
            }
        try:
            url = f"{self.BASE_URL}/{self.instagram_account_id}"
            params = {
                "fields": "id,username,name,profile_picture_url,followers_count",
                "access_token": self.access_token
            }
            res = requests.get(url, params=params, timeout=10)
            data = res.json()
            if "error" in data:
                return {"valid": False, "message": data["error"].get("message", "Unknown error")}
            return {
                "valid": True,
                "username": data.get("username"),
                "name": data.get("name"),
                "followers": data.get("followers_count"),
                "message": f"Connected as @{data.get('username')}"
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
            return {"success": False, "error": f"Video file not found: {file_path}"}

        # Format Instagram Caption: Title + Description + Hashtags
        caption_parts = []
        if title:
            caption_parts.append(title)
        if description:
            caption_parts.append(description)
        if tags:
            tag_str = " ".join([f"#{t.replace(' ', '')}" if not t.startswith("#") else t for t in tags])
            caption_parts.append("\n" + tag_str)
        full_caption = "\n\n".join(caption_parts)[:2200] # IG caption limit 2200

        # Simulation mode if not configured
        if not self.is_configured():
            if progress_callback:
                for pct in range(15, 101, 25):
                    progress_callback(pct, f"Preparing Instagram Reel ({pct}%)...")
                    time.sleep(0.3)
            return {
                "success": True,
                "post_id": f"ig_sim_{int(time.time())}",
                "url": "https://instagram.com/reel/simulated_preview",
                "scheduled": bool(schedule_time_iso),
                "scheduled_for": schedule_time_iso,
                "is_simulation": True,
                "message": "Reel staged in simulation mode. Add Instagram Graph API Token to broadcast live."
            }

        try:
            # Step 1: Create IG Container
            container_url = f"{self.BASE_URL}/{self.instagram_account_id}/media"
            container_payload = {
                "media_type": "REELS",
                "caption": full_caption,
                "share_to_feed": True,
                "access_token": self.access_token
            }

            if schedule_time_iso:
                # Convert ISO to unix timestamp for Meta
                import datetime
                dt = datetime.datetime.fromisoformat(schedule_time_iso.replace("Z", "+00:00"))
                container_payload["scheduled_publish_time"] = int(dt.timestamp())

            if progress_callback:
                progress_callback(30, "Initiating Instagram Reels container...")

            res = requests.post(container_url, data=container_payload, timeout=30)
            res_data = res.json()
            if "error" in res_data:
                return {"success": False, "error": res_data["error"].get("message")}

            container_id = res_data.get("id")

            # Step 2: Poll container status until FINISHED
            if progress_callback:
                progress_callback(60, "Processing video on Instagram servers...")

            status_url = f"{self.BASE_URL}/{container_id}"
            max_wait = 30 # seconds
            waited = 0
            while waited < max_wait:
                time.sleep(3)
                waited += 3
                check_res = requests.get(status_url, params={"fields": "status_code", "access_token": self.access_token})
                status_code = check_res.json().get("status_code")
                if status_code == "FINISHED":
                    break
                elif status_code == "ERROR":
                    return {"success": False, "error": "Instagram failed to process video"}

            # Step 3: If not scheduled, publish container
            if not schedule_time_iso:
                if progress_callback:
                    progress_callback(90, "Publishing Reel live...")
                publish_url = f"{self.BASE_URL}/{self.instagram_account_id}/media_publish"
                pub_res = requests.post(publish_url, data={"creation_id": container_id, "access_token": self.access_token})
                pub_data = pub_res.json()
                if "error" in pub_data:
                    return {"success": False, "error": pub_data["error"].get("message")}
                ig_media_id = pub_data.get("id")
            else:
                ig_media_id = container_id

            if progress_callback:
                progress_callback(100, "Done!")

            return {
                "success": True,
                "post_id": ig_media_id,
                "url": f"https://instagram.com/p/{ig_media_id}",
                "scheduled": bool(schedule_time_iso),
                "scheduled_for": schedule_time_iso,
                "is_simulation": False
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
