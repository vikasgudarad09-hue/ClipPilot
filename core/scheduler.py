"""
Intelligent Cadence Scheduler & Queue Manager
The 'Drip-Feed' engine that distributes bulk videos across future days and weeks.
"""
import os
import json
import uuid
import datetime
from typing import List, Dict, Any, Optional

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

DEFAULT_DAY_PRESETS = {
    1: ["Sun"],
    2: ["Tue", "Fri"],
    3: ["Mon", "Wed", "Fri"],
    4: ["Mon", "Wed", "Fri", "Sun"],
    5: ["Mon", "Tue", "Wed", "Thu", "Fri"],
    6: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    7: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
}

class CadenceScheduler:
    def __init__(self, data_file: str = "data/queue.json"):
        self.data_file = data_file
        self.queue: List[Dict[str, Any]] = []
        self.load_queue()

    def load_queue(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.queue = json.load(f)
            except Exception as e:
                print(f"Error loading queue: {e}")
                self.queue = []
        else:
            self.queue = []

    def save_queue(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.queue, f, indent=2, ensure_ascii=False)

    def calculate_schedule_slots(
        self,
        count: int,
        frequency_per_week: int = 3,
        active_days: Optional[List[str]] = None,
        preferred_time: str = "18:00",
        start_date: Optional[str] = None,
        jitter_minutes: int = 0
    ) -> List[Dict[str, str]]:
        """
        Calculates upcoming schedule datetime slots for 'count' videos based on
        weekly frequency and active posting days.
        """
        if not active_days or len(active_days) == 0:
            active_days = DEFAULT_DAY_PRESETS.get(frequency_per_week, ["Mon", "Wed", "Fri"])

        # Map day strings ("Mon", "Tue", ...) to weekday ints (0=Mon, 6=Sun)
        active_weekdays = sorted([DAY_NAMES.index(d) for d in active_days if d in DAY_NAMES])
        if not active_weekdays:
            active_weekdays = [0, 2, 4] # fallback Mon, Wed, Fri

        # Parse preferred time
        try:
            hour, minute = map(int, preferred_time.split(":"))
        except Exception:
            hour, minute = 18, 0

        # Determine start date
        today = datetime.date.today()
        if start_date:
            try:
                curr_date = datetime.date.fromisoformat(start_date)
            except Exception:
                curr_date = today + datetime.timedelta(days=1)
        else:
            curr_date = today + datetime.timedelta(days=1)

        slots = []
        step_date = curr_date
        import random

        while len(slots) < count:
            if step_date.weekday() in active_weekdays:
                # Add natural humanized jitter if requested
                slot_min = minute
                if jitter_minutes > 0:
                    slot_min += random.randint(-jitter_minutes, jitter_minutes)
                    slot_min = max(0, min(59, slot_min))

                dt = datetime.datetime(
                    step_date.year, step_date.month, step_date.day,
                    hour, slot_min, 0
                )
                
                # Format strings
                iso_str = dt.isoformat()
                human_str = dt.strftime("%A, %d %b %Y at %I:%M %p")
                day_name = dt.strftime("%a")

                slots.append({
                    "iso": iso_str,
                    "human": human_str,
                    "date": dt.strftime("%Y-%m-%d"),
                    "time": dt.strftime("%H:%M"),
                    "day": day_name
                })

            step_date += datetime.timedelta(days=1)

        return slots

    def apply_cadence_to_queue(
        self,
        frequency_per_week: int = 3,
        active_days: Optional[List[str]] = None,
        preferred_time: str = "18:00",
        start_date: Optional[str] = None,
        target_indices: Optional[List[int]] = None
    ):
        """
        Re-dates videos in the queue automatically according to the cadence rules.
        """
        indices_to_schedule = []
        if target_indices is not None:
            indices_to_schedule = target_indices
        else:
            indices_to_schedule = [i for i, item in enumerate(self.queue) if item.get("status") in ["queued", "scheduled"]]

        if not indices_to_schedule:
            return []

        slots = self.calculate_schedule_slots(
            count=len(indices_to_schedule),
            frequency_per_week=frequency_per_week,
            active_days=active_days,
            preferred_time=preferred_time,
            start_date=start_date
        )

        for idx, slot in zip(indices_to_schedule, slots):
            self.queue[idx]["scheduled_time_iso"] = slot["iso"]
            self.queue[idx]["scheduled_time_human"] = slot["human"]
            self.queue[idx]["status"] = "scheduled"

        self.save_queue()
        return slots

    def add_video(
        self,
        file_path: str,
        title: Optional[str] = None,
        description: str = "",
        tags: Optional[List[str]] = None,
        thumbnail_path: Optional[str] = None,
        target_platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Adds a single video to the queue, auto-detecting paired thumbnail and title.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Video file not found: {file_path}")

        file_name = os.path.basename(file_path)
        base_name, ext = os.path.splitext(file_name)
        folder = os.path.dirname(file_path)

        # Auto-detect paired thumbnail if not supplied
        if not thumbnail_path:
            for thumb_ext in [".png", ".jpg", ".jpeg", ".webp"]:
                candidate = os.path.join(folder, f"{base_name}{thumb_ext}")
                if os.path.exists(candidate):
                    thumbnail_path = candidate
                    break

        # Auto-detect paired description text file
        if not description:
            desc_file = os.path.join(folder, f"{base_name}.txt")
            if os.path.exists(desc_file):
                try:
                    with open(desc_file, "r", encoding="utf-8") as f:
                        description = f.read()
                except Exception:
                    pass

        # Clean title
        if not title:
            # Replace underscores and hyphens with spaces and capitalize
            title = base_name.replace("_", " ").replace("-", " ").title()

        file_size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)

        item = {
            "id": str(uuid.uuid4())[:8],
            "file_path": os.path.abspath(file_path),
            "file_name": file_name,
            "file_size_mb": file_size_mb,
            "title": title,
            "description": description or f"Educational guide on {title}. Step-by-step 3D demonstration.",
            "tags": tags or ["3DAnimation", "Educational", "HowTo", "Engineering", "Blender"],
            "thumbnail_path": os.path.abspath(thumbnail_path) if thumbnail_path else "",
            "target_platforms": target_platforms or ["youtube", "instagram", "facebook", "linkedin"],
            "scheduled_time_iso": None,
            "scheduled_time_human": "Not scheduled yet",
            "status": "queued",
            "upload_progress": 0,
            "published_urls": {},
            "error_message": ""
        }

        self.queue.append(item)
        self.save_queue()
        return item

    def remove_video(self, item_id: str) -> bool:
        initial_len = len(self.queue)
        self.queue = [item for item in self.queue if item["id"] != item_id]
        if len(self.queue) != initial_len:
            self.save_queue()
            return True
        return False

    def clear_queue(self):
        self.queue = []
        self.save_queue()

    def update_item(self, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for item in self.queue:
            if item["id"] == item_id:
                item.update(updates)
                self.save_queue()
                return item
        return None
