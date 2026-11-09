"""
YouTube Publisher Module
Handles video uploading, scheduling, thumbnail assignment, and resumable uploads
using the official Google YouTube Data API v3.
"""
import os
import json
import time
from typing import Dict, Any, Optional, Callable
from .base import BasePublisher

class YouTubePublisher(BasePublisher):
    SCOPES = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.force-ssl"
    ]

    def __init__(self, token_path: Optional[str] = None, client_secret_path: Optional[str] = None):
        super().__init__("youtube", "YouTube", "youtube")
        self.token_path = token_path or "data/youtube_token.json"
        self.client_secret_path = client_secret_path or "data/client_secret.json"
        self._service = None
        self._resolve_paths()

    def _resolve_paths(self):
        import sys
        exe_dir = os.path.dirname(sys.executable)
        app_dir = getattr(sys, '_MEIPASS', exe_dir)
        cwd = os.getcwd()

        candidates = [
            self.client_secret_path,
            os.path.join(exe_dir, "data", "client_secret.json"),
            os.path.join(exe_dir, "client_secret.json"),
            os.path.join(app_dir, "data", "client_secret.json"),
            os.path.join(app_dir, "client_secret.json"),
            os.path.join(cwd, "data", "client_secret.json"),
            os.path.join(cwd, "client_secret.json"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "client_secret.json"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "client_secret.json"),
            os.path.join(exe_dir, "data", "client_secret.json.json"),
            os.path.join(exe_dir, "client_secret.json.json"),
            os.path.join(cwd, "data", "client_secret.json.json"),
            os.path.join(cwd, "client_secret.json.json")
        ]
        for c in candidates:
            if c and os.path.exists(c):
                self.client_secret_path = os.path.abspath(c)
                break

        token_candidates = [
            self.token_path,
            os.path.join(exe_dir, "data", "youtube_token.json"),
            os.path.join(exe_dir, "youtube_token.json"),
            os.path.join(cwd, "data", "youtube_token.json"),
            os.path.join(cwd, "youtube_token.json"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "youtube_token.json")
        ]
        for tc in token_candidates:
            if tc and os.path.exists(tc):
                self.token_path = os.path.abspath(tc)
                break

    def is_configured(self) -> bool:
        return os.path.exists(self.token_path) or os.path.exists(self.client_secret_path)

    def get_auth_url(self) -> Optional[str]:
        """Generate Google OAuth URL if client_secret exists."""
        if not os.path.exists(self.client_secret_path):
            return None
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_path, self.SCOPES)
            flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
            auth_url, _ = flow.authorization_url(prompt="consent")
            return auth_url
        except Exception as e:
            print(f"Error generating auth URL: {e}")
            return None

    def save_auth_code(self, code: str) -> bool:
        """Exchange auth code for tokens and save."""
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_path, self.SCOPES)
            flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
            flow.fetch_token(code=code)
            credentials = flow.credentials
            with open(self.token_path, "w", encoding="utf-8") as f:
                f.write(credentials.to_json())
            self._service = None
            return True
        except Exception as e:
            print(f"Error saving auth code: {e}")
            return False

    def authenticate_interactive(self) -> Dict[str, Any]:
        """Runs the 1-click Google OAuth local server flow in browser."""
        self._resolve_paths()
        if not os.path.exists(self.client_secret_path):
            return {"success": False, "message": f"client_secret.json not found in data/ folder ({self.client_secret_path})"}
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_path, self.SCOPES)
            creds = flow.run_local_server(port=0, prompt='consent')
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
            self._service = None
            return {"success": True, "message": "Successfully authenticated with YouTube!"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def _get_service(self):
        self._resolve_paths()
        if self._service is not None:
            return self._service
        if not os.path.exists(self.token_path):
            return None
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request

            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(self.token_path, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())
            self._service = build("youtube", "v3", credentials=creds)
            return self._service
        except Exception as e:
            print(f"Failed to initialize YouTube service: {e}")
            return None

    def validate_credentials(self) -> Dict[str, Any]:
        service = self._get_service()
        if not service:
            return {
                "valid": False,
                "message": "YouTube account not connected yet. Add client_secret.json or log in.",
                "channel_title": None
            }
        try:
            response = service.channels().list(part="snippet,statistics", mine=True).execute()
            items = response.get("items", [])
            if items:
                snippet = items[0]["snippet"]
                stats = items[0]["statistics"]
                return {
                    "valid": True,
                    "message": "Connected successfully",
                    "channel_title": snippet.get("title"),
                    "subscriber_count": stats.get("subscriberCount"),
                    "custom_url": snippet.get("customUrl", "")
                }
            return {"valid": False, "message": "No channel found for this Google account"}
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

        service = self._get_service()
        # If in demo / mock mode without live token:
        if not service:
            # Provide high-fidelity simulation so creators can verify the pipeline
            if progress_callback:
                for pct in range(10, 101, 20):
                    progress_callback(pct, f"Uploading chunk ({pct}%)...")
                    time.sleep(0.3)
            return {
                "success": True,
                "post_id": f"yt_sim_{int(time.time())}",
                "url": f"https://youtu.be/simulated_{int(time.time())}",
                "scheduled": bool(schedule_time_iso),
                "scheduled_for": schedule_time_iso,
                "is_simulation": True,
                "message": "Uploaded in simulation/staging mode. Connect YouTube API keys for live broadcast."
            }

        try:
            from googleapiclient.http import MediaFileUpload
            extra = extra_options or {}
            category_id = str(extra.get("category_id", "27")) # 27 = Education
            
            # YouTube API scheduling rule: If publishAt is set, privacyStatus MUST be 'private'
            status_body = {
                "selfDeclaredMadeForKids": False
            }
            if schedule_time_iso:
                status_body["privacyStatus"] = "private"
                # Ensure UTC 'Z' or standard ISO offset
                publish_at = schedule_time_iso
                if not publish_at.endswith("Z") and "+" not in publish_at:
                    publish_at += "Z"
                status_body["publishAt"] = publish_at
            else:
                status_body["privacyStatus"] = extra.get("privacy", "public")

            body = {
                "snippet": {
                    "title": title[:100], # YouTube max 100 chars
                    "description": description[:5000],
                    "tags": tags[:50],
                    "categoryId": category_id
                },
                "status": status_body
            }

            # 5MB chunk size for resumable uploads
            media = MediaFileUpload(
                file_path,
                chunksize=5 * 1024 * 1024,
                resumable=True
            )

            request = service.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status and progress_callback:
                    pct = int(status.progress() * 100)
                    progress_callback(pct, f"Uploaded {pct}% to YouTube...")

            video_id = response.get("id")
            video_url = f"https://youtu.be/{video_id}"

            # Upload thumbnail if provided and exists
            if thumbnail_path and os.path.exists(thumbnail_path) and video_id:
                try:
                    if progress_callback:
                        progress_callback(99, "Setting video thumbnail...")
                    service.thumbnails().set(
                        videoId=video_id,
                        media_body=MediaFileUpload(thumbnail_path)
                    ).execute()
                except Exception as thumb_err:
                    print(f"Warning: Failed to set thumbnail: {thumb_err}")

            if progress_callback:
                progress_callback(100, "Done!")

            return {
                "success": True,
                "post_id": video_id,
                "url": video_url,
                "scheduled": bool(schedule_time_iso),
                "scheduled_for": schedule_time_iso,
                "is_simulation": False
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
