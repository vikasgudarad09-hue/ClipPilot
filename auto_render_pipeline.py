"""
Autonomous 3D Video Production Agent
Connects directly to Blender 5.2 and FFmpeg.
Renders cinematic 16:9 widescreen videos and 9:16 vertical YouTube Shorts,
generates AI SEO metadata, and queues them into ClipPilot for 1-click publishing.
"""
import os
import sys
import json
import subprocess
import shutil
from typing import Dict, Any, List

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
FFMPEG_EXE = "ffmpeg"
BLEND_FILE = os.path.abspath("hand_pump.blend")
OUTPUT_DIR = os.path.abspath("rendered_videos")
TEMP_DIR = os.path.abspath("temp_render_frames")
STUDIO_DATA_DIR = os.path.abspath(r"OmniPost_Studio\data")
QUEUE_FILE = os.path.join(STUDIO_DATA_DIR, "queue.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(STUDIO_DATA_DIR, exist_ok=True)

# Add OmniPost_Studio to path to use ai_metadata generator
sys.path.insert(0, os.path.abspath("OmniPost_Studio"))
from core.ai_metadata import AIMetadataGenerator

ai_gen = AIMetadataGenerator()

SHOTS = [
    {
        "id": "full_mechanism_16x9",
        "name": "India Mark II Hand Pump - Complete Operation",
        "type": "landscape",
        "res_x": 1920,
        "res_y": 1080,
        "cam_loc": (3.2, -4.8, -3.5),
        "cam_rot": (1.3614, 0.0, 0.6109),
        "cam_lens": 35.0,
        "frame_start": 1,
        "frame_end": 96,
        "filename": "01_india_mark_2_full_mechanism.mp4",
        "topic": "How India Mark II hand pump works without electricity animation",
        "category": "educational"
    },
    {
        "id": "short_handle_9x16",
        "name": "Zero Electricity Hand Pump (Shorts)",
        "type": "shorts",
        "res_x": 1080,
        "res_y": 1920,
        "cam_loc": (1.6, -2.5, 0.75),
        "cam_rot": (1.48, 0.0, 0.58),
        "cam_lens": 36.0,
        "frame_start": 1,
        "frame_end": 96,
        "filename": "02_short_zero_electricity_pump.mp4",
        "topic": "How to pump water with ZERO electricity #Shorts",
        "category": "educational"
    },
    {
        "id": "short_valve_9x16",
        "name": "Secret Underground Valve (Shorts)",
        "type": "shorts",
        "res_x": 1080,
        "res_y": 1920,
        "cam_loc": (1.2, -2.0, -11.4),
        "cam_rot": (1.57, 0.0, 0.52),
        "cam_lens": 45.0,
        "frame_start": 1,
        "frame_end": 96,
        "filename": "03_short_secret_underground_valve.mp4",
        "topic": "The secret non-return valve inside a deep well hand pump #Shorts",
        "category": "educational"
    }
]

def render_shot_with_blender(shot: Dict[str, Any], force_re_render: bool = False) -> str:
    """Renders PNG frames for a shot in Blender using EEVEE with smart caching."""
    shot_temp_dir = os.path.join(TEMP_DIR, shot["id"])
    target_count = shot["frame_end"] - shot["frame_start"] + 1

    if not force_re_render and os.path.exists(shot_temp_dir):
        existing_frames = [f for f in os.listdir(shot_temp_dir) if f.startswith("frame_") and f.endswith(".png")]
        if len(existing_frames) >= target_count:
            print(f"[*] Frames already rendered ({len(existing_frames)} frames found for '{shot['name']}'). Reusing frames.")
            return shot_temp_dir

    if os.path.exists(shot_temp_dir):
        shutil.rmtree(shot_temp_dir, ignore_errors=True)
    os.makedirs(shot_temp_dir, exist_ok=True)

    # Script passed into Blender to configure camera and render
    blender_script = f"""
import bpy
import os

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = {shot["res_x"]}
scene.render.resolution_y = {shot["res_y"]}
scene.render.resolution_percentage = 100
scene.render.fps = 24

scene.frame_start = {shot["frame_start"]}
scene.frame_end = {shot["frame_end"]}

# Setup Camera
cam_obj = bpy.data.objects.get('Main_Camera')
if not cam_obj:
    cam_data = bpy.data.cameras.new('Main_Camera')
    cam_obj = bpy.data.objects.new('Main_Camera', cam_data)
    scene.collection.objects.link(cam_obj)

cam_obj.location = {shot["cam_loc"]}
cam_obj.rotation_euler = {shot["cam_rot"]}
cam_obj.data.lens = {shot["cam_lens"]}
scene.camera = cam_obj

# Output settings (PNG frames)
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.color_depth = '8'
scene.render.filepath = os.path.join(r'{shot_temp_dir}', 'frame_')

print('[BLENDER] Rendering frames {shot["frame_start"]} to {shot["frame_end"]}...')
bpy.ops.render.render(animation=True)
print('[BLENDER] Finished frame render!')
"""
    script_path = os.path.join(TEMP_DIR, f"render_{shot['id']}.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(blender_script)

    print(f"\n[+] Launching Blender 5.2 for '{shot['name']}' ({shot['res_x']}x{shot['res_y']})...")
    cmd = [BLENDER_EXE, "-b", BLEND_FILE, "-P", script_path]
    subprocess.run(cmd, check=True)
    return shot_temp_dir

def compile_frames_to_mp4(shot_temp_dir: str, output_mp4: str) -> bool:
    """Compiles PNG frame sequence to high quality H.264 MP4 with FFmpeg."""
    print(f"[+] Compiling frames with FFmpeg into: {os.path.basename(output_mp4)}...")
    input_pattern = os.path.join(shot_temp_dir, "frame_%04d.png")
    
    cmd = [
        FFMPEG_EXE, "-y",
        "-framerate", "24",
        "-i", input_pattern,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "20",
        output_mp4
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return res.returncode == 0

def extract_thumbnail(shot_temp_dir: str, thumb_path: str):
    """Copies a key frame (frame 48) as custom thumbnail."""
    frame_48 = os.path.join(shot_temp_dir, "frame_0048.png")
    if os.path.exists(frame_48):
        shutil.copyfile(frame_48, thumb_path)
    else:
        # Fallback to first available frame
        frames = sorted([f for f in os.listdir(shot_temp_dir) if f.endswith(".png")])
        if frames:
            shutil.copyfile(os.path.join(shot_temp_dir, frames[0]), thumb_path)

def add_to_clippilot_queue(video_path: str, thumb_path: str, title: str, desc: str, tags: List[str], platforms: List[str]):
    """Injects the rendered video directly into ClipPilot's persistent queue."""
    queue = []
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                queue = json.load(f)
        except Exception:
            queue = []

    # Check if already in queue
    for item in queue:
        if item.get("file_path") == video_path:
            print(f"[*] Already in queue: {os.path.basename(video_path)}")
            return

    import uuid
    import time
    file_size_mb = round(os.path.getsize(video_path) / (1024 * 1024), 2)
    new_item = {
        "id": f"vid_{uuid.uuid4().hex[:8]}",
        "file_path": video_path,
        "file_name": os.path.basename(video_path),
        "file_size_mb": file_size_mb,
        "title": title,
        "description": desc,
        "tags": tags,
        "thumbnail_path": thumb_path if os.path.exists(thumb_path) else None,
        "target_platforms": platforms,
        "status": "queued",
        "created_at": time.time(),
        "scheduled_time_iso": None,
        "scheduled_time_human": None
    }
    queue.append(new_item)
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)
    print(f"[✓] Queued in ClipPilot: {title}")

def run_pipeline(single_shot_id: str = None):
    print("="*60)
    print("   ✈️  CLIPPILOT AUTONOMOUS 3D VIDEO PRODUCTION AGENT")
    print("="*60)

    shots_to_render = SHOTS
    if single_shot_id:
        shots_to_render = [s for s in SHOTS if s["id"] == single_shot_id]

    rendered_items = []

    for shot in shots_to_render:
        out_mp4 = os.path.join(OUTPUT_DIR, shot["filename"])
        thumb_png = os.path.join(OUTPUT_DIR, shot["filename"].replace(".mp4", "_thumb.png"))

        # Step 1: Render frames in Blender
        shot_frames_dir = render_shot_with_blender(shot)

        # Step 2: Compile to MP4 with FFmpeg
        compile_frames_to_mp4(shot_frames_dir, out_mp4)

        # Step 3: Extract thumbnail
        extract_thumbnail(shot_frames_dir, thumb_png)

        # Step 4: Generate High-CTR SEO Metadata
        print(f"[+] Generating Multilingual AI SEO for '{shot['name']}'...")
        metadata = ai_gen.generate(
            topic_or_title=shot["topic"],
            language="hinglish" if shot["type"] == "shorts" else "english",
            category=shot["category"]
        )

        title = metadata["youtube"]["title"]
        desc = metadata["youtube"]["description"]
        tags = metadata["youtube"]["tags"]
        platforms = ["youtube"]

        # Step 5: Inject directly into ClipPilot queue
        add_to_clippilot_queue(out_mp4, thumb_png, title, desc, tags, platforms)
        rendered_items.append({"title": title, "path": out_mp4})

    print("\n" + "="*60)
    print(f"🎉 PIPELINE COMPLETE! Successfully produced {len(rendered_items)} videos.")
    print("All videos are queued in ClipPilot and ready to schedule/publish!")
    print("="*60)

if __name__ == "__main__":
    shot_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_pipeline(shot_arg)
