"""
ClipPilot - License and Usage Manager
Handles Free Trial (5 videos) and Pro Lifetime license activation.
"""
import os
import json
import hmac
import hashlib
from typing import Dict, Any, Tuple

LICENSE_SALT = "CLIPPILOT-PRO-SECRET-SALT-2026-HQ"
MASTER_KEYS = [
    "CP-PRO-VIP-UNLIMITED-2026",
    "CP-PRO-FOUNDER-LIFETIME",
    "CP-PRO-VIKAS-HQ-MASTER"
]

class LicenseManager:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.license_file = os.path.join(data_dir, "license.json")
        self.usage_file = os.path.join(data_dir, "usage.json")
        self.free_limit = 5
        os.makedirs(self.data_dir, exist_ok=True)

    def _generate_checksum(self, serial: str) -> str:
        """Generates a 12-character HMAC checksum for a serial string."""
        h = hmac.new(LICENSE_SALT.encode('utf-8'), serial.upper().strip().encode('utf-8'), hashlib.sha256)
        digest = h.hexdigest().upper()
        return f"{digest[:4]}-{digest[4:8]}-{digest[8:12]}"

    def generate_license_key(self, customer_id: str) -> str:
        """
        Creates a license key for a customer (email, name, or serial).
        Format: CP-PRO-<SERIAL>-<CHECKSUM>
        """
        clean_id = "".join(c for c in customer_id.upper() if c.isalnum())[:8].ljust(8, 'X')
        checksum = self._generate_checksum(clean_id)
        return f"CP-PRO-{clean_id}-{checksum}"

    def verify_license_key(self, key: str) -> bool:
        """Verifies if a license key is cryptographically valid."""
        clean_key = key.strip().upper()
        if clean_key in MASTER_KEYS:
            return True

        parts = clean_key.split("-")
        # Format: CP-PRO-<SERIAL>-<PART1>-<PART2>-<PART3> (6 parts total)
        if len(parts) == 6 and parts[0] == "CP" and parts[1] == "PRO":
            serial = parts[2]
            provided_checksum = f"{parts[3]}-{parts[4]}-{parts[5]}"
            expected = self._generate_checksum(serial)
            return provided_checksum == expected

        # Format: CP-PRO-<SERIAL>-<PART1>-<PART2> (5 parts total)
        if len(parts) == 5 and parts[0] == "CP" and parts[1] == "PRO":
            serial = parts[2]
            provided_checksum = f"{parts[3]}-{parts[4]}"
            expected = self._generate_checksum(serial)
            return expected.startswith(provided_checksum)

        # Also support 4-part: CP-PRO-<SERIAL>-<HASH>
        if len(parts) == 4 and parts[0] == "CP" and parts[1] == "PRO":
            serial = parts[2]
            provided_hash = parts[3]
            expected = self._generate_checksum(serial).replace("-", "")
            return expected.startswith(provided_hash)

        return False

        return False

    def is_pro_active(self) -> bool:
        """Checks if a verified Pro license is active on this machine."""
        if not os.path.exists(self.license_file):
            return False
        try:
            with open(self.license_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                key = data.get("key", "")
                return self.verify_license_key(key)
        except Exception:
            return False

    def activate(self, key: str) -> Tuple[bool, str]:
        """Attempts to activate a license key."""
        if not key or not self.verify_license_key(key):
            return False, "Invalid license key. Please check your purchase email or purchase a key."

        data = {
            "key": key.strip().upper(),
            "activated": True,
            "tier": "Pro Lifetime"
        }
        with open(self.license_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return True, "ClipPilot Pro Lifetime successfully activated!"

    def get_published_count(self) -> int:
        """Returns the total number of videos published in free trial."""
        if not os.path.exists(self.usage_file):
            return 0
        try:
            with open(self.usage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return int(data.get("published_count", 0))
        except Exception:
            return 0

    def increment_published_count(self, count: int = 1):
        """Increments published video count."""
        current = self.get_published_count()
        new_count = current + count
        with open(self.usage_file, "w", encoding="utf-8") as f:
            json.dump({"published_count": new_count}, f, indent=2)

    def get_status(self) -> Dict[str, Any]:
        """Returns the full plan and usage status."""
        is_pro = self.is_pro_active()
        published_count = self.get_published_count()
        remaining = max(0, self.free_limit - published_count) if not is_pro else 999999

        return {
            "is_pro": is_pro,
            "plan_name": "Pro Lifetime" if is_pro else "Free Starter",
            "free_limit": self.free_limit,
            "published_count": published_count,
            "remaining_free": remaining,
            "can_publish": is_pro or (remaining > 0)
        }

    def can_publish_batch(self, count: int) -> Tuple[bool, str]:
        """Checks if a batch of videos is allowed under the current plan."""
        if self.is_pro_active():
            return True, "Pro active"

        published = self.get_published_count()
        remaining = max(0, self.free_limit - published)

        if remaining <= 0:
            return False, f"You have reached the Free Starter limit ({self.free_limit}/{self.free_limit} videos published). Upgrade to ClipPilot Pro for unlimited bulk publishing!"

        if count > remaining:
            return False, f"Your Free Starter plan has {remaining} video upload(s) remaining, but you queued {count}. Upgrade to ClipPilot Pro to publish unlimited videos at once!"

        return True, "Allowed"
