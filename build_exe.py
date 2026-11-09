"""
Build script to package OmniPost Studio into a standalone Windows .exe
"""
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def build():
    print("Building ClipPilot Windows Executable...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=ClipPilot",
        "--onedir",
        "--clean",
        "--noconfirm",
        f"--add-data={os.path.join(BASE_DIR, 'static')};static",
        f"--add-data={os.path.join(BASE_DIR, 'core')};core",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.protocols.websockets.auto",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=googleapiclient.discovery",
        "--hidden-import=google_auth_oauthlib.flow",
        os.path.join(BASE_DIR, "app.py")
    ]
    print("Running command:", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=BASE_DIR)
    if proc.returncode == 0:
        print("\nSUCCESS! Executable built at: dist/ClipPilot/ClipPilot.exe")
    else:
        print("\nBuild failed with code:", proc.returncode)

if __name__ == "__main__":
    build()
