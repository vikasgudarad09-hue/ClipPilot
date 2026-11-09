"""
Publisher Registry
Provides unified access to all platform publishers.
"""
import os
from typing import Dict, Optional
from .base import BasePublisher
from .youtube import YouTubePublisher
from .instagram import InstagramPublisher
from .facebook import FacebookPublisher
from .linkedin import LinkedInPublisher
from .twitter_x import TwitterPublisher
from .other_platforms import ThreadsPublisher, PinterestPublisher, TikTokPublisher

def get_all_publishers(data_dir: Optional[str] = None) -> Dict[str, BasePublisher]:
    if data_dir:
        token_path = os.path.join(data_dir, "youtube_token.json")
        client_secret_path = os.path.join(data_dir, "client_secret.json")
        yt = YouTubePublisher(token_path=token_path, client_secret_path=client_secret_path)
    else:
        yt = YouTubePublisher()

    # 100% 1-Click Login Only - Zero token prompt friction
    return {
        "youtube": yt
    }
