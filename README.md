# ✈️ ClipPilot — Put Your Video Publishing on Autopilot
### 🇮🇳 Next-Gen Desktop Video Bulk Auto-Scheduler & Multilingual AI SEO Engine for Creators

[![Website](https://img.shields.io/badge/Website-clippilot--studio.web.app-blue?style=for-the-badge&logo=google-chrome&logoColor=white)](https://clippilot-studio.web.app)
[![Download](https://img.shields.io/badge/Download-Windows%20.exe-emerald?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/vikasgudarad09-hue/ClipPilot/releases/download/v1.0.0/ClipPilot_Setup_v1.0.exe)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?style=for-the-badge&logo=windows11&logoColor=white)](https://clippilot-studio.web.app)
[![License](https://img.shields.io/badge/License-Proprietary%20%2F%20Commercial-purple?style=for-the-badge)](https://clippilot-studio.web.app/terms.html)

---

## 💡 What is ClipPilot?

**ClipPilot** is a high-performance desktop application designed for **YouTubers, 3D animators, educators, and content creators** who produce batches of video content and want to automate their publishing workflow. 

Instead of spending hours manually uploading, writing titles, tags, and scheduling 10–50 videos one by one in YouTube Studio, ClipPilot lets you drop your entire batch into one screen, set your weekly cadence rule (e.g. *3 videos a week on Mon/Wed/Fri at 6:30 PM*), generate high-CTR multilingual AI titles and tags, and **schedule the entire month in 1 single click**.

---

## 🌟 Key Features

### 1. ⏱️ Smart "Drip-Feed" Bulk Cadence Scheduler
- Drop **10, 20, or 50 videos** at once into the queue.
- Choose your cadence: e.g. *2–3 videos per week on chosen active days at peak viewer hours (6:30 PM IST)*.
- With **1 click**, ClipPilot automatically calculates future publishing dates across upcoming weeks and attaches `publishAt` timestamps.
- **Humanized Time Jitter**: Adds natural ±3–5 minute randomized offsets to avoid robotic posting patterns.

### 2. 🔴 Zero-Token 1-Click YouTube Integration
- No manual API keys, client secrets, or complex cloud console configurations required for end users.
- Built-in official Google OAuth 2.0 flow: simply click **"🔴 Sign in with Google"** to link your YouTube channel instantly.
- Supports both standard 16:9 widescreen videos and 9:16 **YouTube Shorts** with automatic aspect ratio detection.
- Auto-pairs matching custom thumbnail files (`video.png` paired to `video.mp4`).

### 3. ✨ Multilingual AI SEO Generator
- Built specifically for Indian and international creators.
- Generates high-CTR video titles, formatted descriptions with timestamps, and high-reach hashtags in:
  - **Hinglish** (High reach for Indian creator audiences)
  - **Hindi** (Devanagari educational & formal tone)
  - **English** (Global SEO optimization)

### 4. 🔒 100% Private, Local & Secure Architecture
- **Zero Cloud Middleman**: Your heavy multi-gigabyte video files stay strictly on your local PC and stream directly to YouTube's official servers.
- **Resumable Chunked Uploads**: Built on YouTube API v3 chunked upload protocol. If your Wi-Fi or broadband flickers mid-upload, it pauses and auto-resumes seamlessly without restarting from 0%.
- **Local Loopback CORS Isolation**: Backend is hardened with strict CORS restricted to localhost (`127.0.0.1:8765`), eliminating cross-site request forgery and port scanning risks.
- **Hardware Machine Binding**: License activation is bound cryptographically to machine hardware fingerprints using HMAC-SHA256 signatures.

---

## 📊 Plan Comparison

| Feature | Free Starter (₹0) | Pro Lifetime (₹499 / $9) |
| :--- | :---: | :---: |
| **Video Uploads** | **5 Free Videos (Full Test)** | **UNLIMITED Bulk Uploads** |
| **Smart Cadence Engine** | ✅ Included | ✅ Priority Drip-Feed |
| **1-Click YouTube OAuth** | ✅ Included | ✅ Multi-Channel Ready |
| **Multilingual AI SEO** | ✅ Standard | ✅ UNLIMITED AI Generations |
| **Custom Thumbnails** | ✅ Included | ✅ Auto-Pairing |
| **License Duration** | Free Forever | **Lifetime (One-Time Payment)** |
| **Updates & Support** | Community | **Lifetime Updates & Priority Support** |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **APIs**: Google APIs Client, YouTube Data API v3, Google OAuth Lib
- **Frontend**: Modern Responsive HTML5 / CSS3 / Vanilla JavaScript (Dark Mode Creator UI)
- **Packaging**: PyInstaller (Standalone Windows Binary) & Inno Setup 6 (Installer Compiler)
- **Hosting**: Firebase Hosting (`clippilot-studio.web.app`)
- **Security**: HMAC-SHA256 Cryptographic Signatures, Web Crypto API, Path Traversal Guards, Loopback CORS

---

## 🚀 Running from Source

### Prerequisites
- Python 3.10 or higher installed on Windows.

### Installation
```bash
# Clone the repository
git clone https://github.com/vikasgudarad09-hue/ClipPilot.git
cd ClipPilot

# Install dependencies
pip install -r requirements.txt

# Launch ClipPilot Studio
python app.py
```
ClipPilot will launch on `http://127.0.0.1:8765` and automatically open your default browser.

---

## 📦 Building the Standalone Windows Installer

To compile your own standalone `.exe` installer:

```powershell
# 1. Compile binary with PyInstaller
python build_exe.py

# 2. Compile setup wizard with Inno Setup
& "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" installer.iss
```
The output installer will be generated at `dist_installer\ClipPilot_Setup_v1.0.exe`.

---

## 🔑 License Key Management (For Admins)

To generate a Pro Lifetime key for a customer after purchase:

```powershell
python generate_key.py customer_email@gmail.com
```

---

## 📬 Contact & Support

- **Website**: [clippilot-studio.web.app](https://clippilot-studio.web.app)
- **Checkout**: [clippilot-studio.web.app/checkout.html](https://clippilot-studio.web.app/checkout.html)
- **Support & Inquiries**: `gudaradvikas09@gmail.com`
- **Developer**: Vikas Prabhu Gudarad 🇮🇳

---

*© 2026 ClipPilot. All rights reserved. YouTube and Google are registered trademarks of Google LLC.*
