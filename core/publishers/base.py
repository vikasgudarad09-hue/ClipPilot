"""
Base Publisher Module
Defines the unified interface for all social media video publishing adapters.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable

class BasePublisher(ABC):
    def __init__(self, platform_id: str, display_name: str, icon: str):
        self.platform_id = platform_id
        self.display_name = display_name
        self.icon = icon
        self.config: Dict[str, Any] = {}

    def set_config(self, config: Dict[str, Any]):
        self.config = config or {}

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if user has provided required tokens/credentials."""
        pass

    @abstractmethod
    def validate_credentials(self) -> Dict[str, Any]:
        """Test API connection and return account info."""
        pass

    @abstractmethod
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
        """
        Upload and optionally schedule the video.
        Returns dict with keys:
          - success: bool
          - post_id: Optional[str]
          - url: Optional[str]
          - error: Optional[str]
          - scheduled: bool
        """
        pass

    def get_platform_info(self) -> Dict[str, Any]:
        return {
            "id": self.platform_id,
            "name": self.display_name,
            "icon": self.icon,
            "is_configured": self.is_configured()
        }
