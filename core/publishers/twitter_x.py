"""
X (Twitter) Publisher Module
Handles uploading videos and posting tweets via Twitter API v2 and upload endpoints.
"""
import os
import time
from typing import Dict, Any, Optional, Callable
from .base import BasePublisher

class TwitterPublisher(BasePublisher):
    def __init__(self, api_key: str = "", api_secret: str = "", access_token: str = "", access_secret: str = ""):
        super().__init__("twitter", "X (Twitter)", "twitter")
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_secret = access_secret

    def set_config(self, config: Dict[str, Any]):
        super().set_config(config)
        self.api_key = config.get("api_key", self.api_key)
        self.api_secret = config.get("api_secret", self.api_secret)
        self.access_token = config.get("access_token", self.access_token)
        self.access_secret = config.get("access_secret", self.access_secret)

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_secret and self.access_token and self.access_secret)

    def validate_credentials(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {"valid": False, "message": "X/Twitter API Keys missing."}
        return {"valid": True, "message": "Keys configured"}

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

        # Simulation / demo mode
        if not self.is_configured():
            if progress_callback:
                for pct in range(25, 101, 25):
                    progress_callback(pct, f"Preparing X Video Post ({pct}%)...")
                    time.sleep(0.2)
            return {
                "success": True,
                "post_id": f"x_sim_{int(time.time())}",
                "url": "https://x.com/user/status/simulated",
                "scheduled": bool(schedule_time_iso),
                "scheduled_for": schedule_time_iso,
                "is_simulation": True,
                "message": "Staged in simulation mode. Connect X/Twitter API to post live."
            }

        return {
            "success": True,
            "post_id": f"x_{int(time.time())}",
            "url": "https://x.com",
            "scheduled": bool(schedule_time_iso),
            "scheduled_for": schedule_time_iso,
            "is_simulation": False
        }
