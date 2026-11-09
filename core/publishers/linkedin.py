"""
LinkedIn Publisher Module
Handles uploading and publishing videos to LinkedIn personal profiles
or company pages via the LinkedIn REST API.
"""
import os
import time
import requests
from typing import Dict, Any, Optional, Callable
from .base import BasePublisher

class LinkedInPublisher(BasePublisher):
    def __init__(self, access_token: str = "", author_urn: str = ""):
        super().__init__("linkedin", "LinkedIn (Video & Post)", "linkedin")
        self.access_token = access_token
        self.author_urn = author_urn  # e.g., "urn:li:person:XXXX" or "urn:li:organization:YYYY"

    def set_config(self, config: Dict[str, Any]):
        super().set_config(config)
        self.access_token = config.get("access_token", self.access_token)
        self.author_urn = config.get("author_urn", self.author_urn)

    def is_configured(self) -> bool:
        return bool(self.access_token and self.author_urn)

    def validate_credentials(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {"valid": False, "message": "LinkedIn Access Token or Author URN missing."}
        try:
            headers = {"Authorization": f"Bearer {self.access_token}", "X-Restli-Protocol-Version": "2.0.0"}
            res = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers, timeout=10)
            data = res.json()
            if "name" in data or "sub" in data:
                return {"valid": True, "name": data.get("name", "LinkedIn User"), "message": f"Connected as {data.get('name')}"}
            return {"valid": False, "message": "Invalid token or permissions."}
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
                for pct in range(25, 101, 25):
                    progress_callback(pct, f"Preparing LinkedIn Post ({pct}%)...")
                    time.sleep(0.2)
            return {
                "success": True,
                "post_id": f"li_sim_{int(time.time())}",
                "url": "https://linkedin.com/feed/update/simulated",
                "scheduled": bool(schedule_time_iso),
                "scheduled_for": schedule_time_iso,
                "is_simulation": True,
                "message": "Staged in simulation mode. Add LinkedIn API token to post live."
            }

        try:
            # Multi-step LinkedIn Video API
            # Step 1: Initialize upload
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "LinkedIn-Version": "202401",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            file_size = os.path.getsize(file_path)
            init_url = "https://api.linkedin.com/rest/videos?action=initializeUpload"
            init_body = {
                "initializeUploadRequest": {
                    "owner": self.author_urn,
                    "fileSizeBytes": file_size,
                    "uploadCaptions": False,
                    "uploadThumbnail": False
                }
            }
            if progress_callback:
                progress_callback(20, "Initializing LinkedIn video upload...")

            res = requests.post(init_url, headers=headers, json=init_body, timeout=20)
            data = res.json()
            upload_instructions = data.get("value", {}).get("uploadInstructions", [])
            video_urn = data.get("value", {}).get("video")

            if not upload_instructions or not video_urn:
                return {"success": False, "error": f"Failed to initialize LinkedIn upload: {data}"}

            upload_url = upload_instructions[0].get("uploadUrl")
            if progress_callback:
                progress_callback(50, "Sending video data to LinkedIn...")

            with open(file_path, "rb") as f:
                put_headers = {"Content-Type": "application/octet-stream"}
                requests.put(upload_url, headers=put_headers, data=f, timeout=120)

            # Step 2: Create post with video URN
            if progress_callback:
                progress_callback(85, "Creating LinkedIn post...")

            post_url = "https://api.linkedin.com/rest/posts"
            text_content = f"{title}\n\n{description}"
            if tags:
                text_content += "\n\n" + " ".join([f"#{t.replace(' ', '')}" for t in tags])

            post_body = {
                "author": self.author_urn,
                "commentary": text_content[:3000],
                "visibility": "PUBLIC",
                "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
                "content": {
                    "media": {
                        "title": title[:200],
                        "id": video_urn
                    }
                },
                "lifecycleState": "PUBLISHED"
            }

            post_res = requests.post(post_url, headers=headers, json=post_body, timeout=20)
            if post_res.status_code in [200, 201]:
                return {
                    "success": True,
                    "post_id": video_urn,
                    "url": "https://linkedin.com/feed/",
                    "scheduled": bool(schedule_time_iso),
                    "scheduled_for": schedule_time_iso,
                    "is_simulation": False
                }
            return {"success": False, "error": post_res.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
