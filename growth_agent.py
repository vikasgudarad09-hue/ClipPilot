"""
Autonomous Creator Outreach & Growth Agent
Finds creator niches, drafts high-converting personalized pitches,
tracks leads, and generates complete multi-platform viral distribution kits.
"""
import os
import sys
import json
import time
from typing import Dict, Any, List

DATA_DIR = os.path.abspath("data")
CAMPAIGNS_DIR = os.path.abspath("campaigns")
LEADS_FILE = os.path.join(DATA_DIR, "leads.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CAMPAIGNS_DIR, exist_ok=True)

DEFAULT_LEADS = [
    {
        "id": "lead_01",
        "name": "Tech & 3D Animation Creators",
        "channel_type": "Blender & Engineering Animators",
        "niche": "3d_animation",
        "estimated_frequency": "2-3 videos/week",
        "status": "Ready to Pitch",
        "contact_type": "Instagram / Twitter / Email"
    },
    {
        "id": "lead_02",
        "name": "Educational 'How-It-Works' YouTubers",
        "channel_type": "Science & Mechanical Explainer Channels",
        "niche": "education",
        "estimated_frequency": "1-2 long videos + 5 shorts/week",
        "status": "Ready to Pitch",
        "contact_type": "About Page Business Email"
    },
    {
        "id": "lead_03",
        "name": "YouTube Automation & Faceless Channels",
        "channel_type": "Shorts / Reels Clipping & Repurposing",
        "niche": "faceless_shorts",
        "estimated_frequency": "1-3 shorts/day",
        "status": "Ready to Pitch",
        "contact_type": "Discord & Twitter DMs"
    },
    {
        "id": "lead_04",
        "name": "Freelance Video Editors & Agencies",
        "channel_type": "Client Channel Management",
        "niche": "agencies",
        "estimated_frequency": "10-20 client videos/month",
        "status": "Ready to Pitch",
        "contact_type": "LinkedIn & Upwork/Fiverr"
    }
]

def load_leads() -> List[Dict[str, Any]]:
    if not os.path.exists(LEADS_FILE):
        save_leads(DEFAULT_LEADS)
        return DEFAULT_LEADS
    try:
        with open(LEADS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_LEADS

def save_leads(leads: List[Dict[str, Any]]):
    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2)

def generate_pitch(lead: Dict[str, Any], creator_name: str = None) -> str:
    name = creator_name or lead.get("name", "Creator")
    niche = lead.get("niche", "general")

    if niche == "3d_animation":
        pitch = f"""
Subject: Love your 3D animations! Quick question on your upload workflow

Hey {name},

Big fan of your 3D animation work. I know firsthand how much time rendering and post-production takes. 

One thing that used to kill my week was manually uploading 10-15 video clips and shorts to YouTube Studio, typing titles, and scheduling dates one by one.

I built a lightweight Windows tool called ClipPilot (made in India) specifically for creators who render batches. You drop your videos, set your posting schedule (e.g., 3 videos a week on Mon/Wed/Fri at 6:30 PM), and it distributes and schedules the entire batch to YouTube in 1 click.

You can try 5 free video uploads here:
https://clippilot-studio.web.app

Would love your feedback!
Best,
Vikas Prabhu Gudarad
"""
    elif niche == "faceless_shorts":
        pitch = f"""
Subject: Save 2 hours/week bulk scheduling your Shorts

Hey {name},

Noticed you publish Shorts consistently. Managing high-frequency uploads in YouTube Studio gets tedious fast.

I built ClipPilot — a desktop tool that automates bulk scheduling with smart drip-feed cadences. You drop 20 Shorts at once, pick your cadence (e.g. 2 shorts/day), and it publishes them on autopilot.

Runs locally on your PC, 1-click Google login, and 100% free to test (5 video uploads):
👉 https://clippilot-studio.web.app

Hope it helps you scale your publishing!
"""
    elif niche == "agencies":
        pitch = f"""
Subject: Automate YouTube client publishing (Zero monthly fees)

Hey {name},

If you manage YouTube video publishing for clients, manually setting schedule dates, tags, and thumbnails for 20+ videos a week takes hours.

We built ClipPilot: a desktop bulk publishing engine.
- Drop 20 client videos at once
- 1-Click Smart Cadence Scheduler (distributes across upcoming weeks)
- Multilingual AI SEO generator (Hinglish/Hindi/English)
- Zero monthly subscription fees

Test it with 5 free video uploads:
https://clippilot-studio.web.app

Best,
Vikas Prabhu Gudarad
"""
    else:
        pitch = f"""
Subject: Quick tool to automate your YouTube upload schedule

Hey {name},

Love your content. I'm a developer from India and I built a free Windows desktop tool called ClipPilot that automates bulk scheduling for YouTube.

Instead of uploading videos one by one, you drop your batch into ClipPilot, set your weekly cadence rule (e.g. 3 videos/week at peak hours), and it schedules everything automatically in 1 click.

You can test 5 video uploads free here:
https://clippilot-studio.web.app

Let me know what you think!
"""
    return pitch.strip()

def generate_weekly_distribution_kit() -> str:
    """Generates ready-to-publish social campaigns for Reddit, Twitter, and LinkedIn."""
    kit = f"""# 🚀 ClipPilot Weekly Distribution & Viral Growth Kit
*Generated on {time.strftime('%Y-%m-%d')} for Vikas Prabhu Gudarad*
*Website:* https://clippilot-studio.web.app | *Checkout:* https://clippilot-studio.web.app/checkout.html

---

## 📌 Campaign 1: Reddit r/NewTubers (The Creator Burnout Angle)
**Target:** https://reddit.com/r/NewTubers
**Title:** I got tired of manually uploading 15 videos to YouTube one by one, so I built a free desktop tool to fix it

**Body:**
Hey creators,

One of the most exhausting parts of my week was rendering a batch of videos and then sitting in YouTube Studio for 2 hours uploading each video, writing descriptions, picking thumbnails, and scheduling dates one by one.

So I spent the last few weeks building **ClipPilot** — a lightweight Windows tool that lets you drop 10–20 videos at once, pick your schedule rule (e.g. 3 videos a week on Mon/Wed/Fri at 6:30 PM), and it distributes and schedules the entire batch to YouTube automatically with 1 click.

- Runs 100% locally on your PC (your files never leave your computer)
- Official 1-click Google OAuth (zero token hassle)
- Multilingual AI SEO for high-CTR titles and hashtags
- Free Starter plan includes 5 free video uploads to test

Check it out free here: https://clippilot-studio.web.app

Would love any feedback or feature requests from fellow creators!

---

## 📌 Campaign 2: Reddit r/blender & r/educationalgifs (The 3D Animation Showcase)
**Target:** https://reddit.com/r/blender & https://reddit.com/r/educationalgifs
**Title:** 3D Animation: How an India Mark II Hand Pump lifts water from deep underground with ZERO electricity

**Body:**
Hey everyone! Here is a mechanical 3D animation I rendered in Blender showing the internal working of an India Mark II deep-well hand pump.

Notice how the foot valve and plunger valve work in alternating cycles:
1. Downstroke: Plunger valve opens, water enters upper chamber while foot valve stays closed.
2. Upstroke: Plunger valve closes, lifting the entire column of water up the riser pipe, while foot valve opens to pull in fresh water from the aquifer.

Full breakdown & YouTube video scheduled using ClipPilot: https://clippilot-studio.web.app

---

## 📌 Campaign 3: Twitter / X Thread (High Engagement)
**Tweet 1 (Hook):**
Uploading 20 videos to YouTube manually takes 2 hours of boring repetitive work.

So I built a tool called ClipPilot that automates the entire publishing schedule in 1 click.

Here is how it works (and how you can use it free): 🧵👇

**Tweet 2 (The Problem):**
Creators spend 80% of their energy making great content, and then burn out doing:
- Manual file uploads
- Typing descriptions & tags
- Calculating future schedule dates on a calendar
- Setting up thumbnails one by one

**Tweet 3 (The Solution):**
ClipPilot fixes this:
1. Drop your entire video batch
2. Pick your cadence (e.g., 3x/week at 6:30 PM)
3. AI generates high-CTR titles & hashtags in Hinglish/English
4. Hit "Publish All" — done in 10 seconds.

**Tweet 4 (Privacy & Security):**
Zero cloud middleman. Your heavy video files stream directly from your PC to YouTube via official Google API.

**Tweet 5 (Call to Action):**
100% free to test with 5 uploads.
Download for Windows: https://clippilot-studio.web.app
Give it a try and let me know your thoughts!

---

## 📌 Campaign 4: LinkedIn Post (Aimed at Video Editors & Agency Owners)
**Post Body:**
If you edit videos or manage YouTube channels for clients, you know the pain:

Friday evening arrives. You have 15 client videos rendered. Now you have to sit in YouTube Studio for 90 minutes manually setting titles, tags, thumbnails, and schedule dates.

I built **ClipPilot** to solve this:
- Drop 15 videos into the dashboard
- Set your rule: e.g. "3 videos/week on Mon, Wed, Fri at 6:30 PM"
- 1-Click scheduling distributes all dates across future weeks automatically
- Local Windows app, zero monthly subscription fees

Try 5 free video uploads here: https://clippilot-studio.web.app

#VideoEditing #YouTubeGrowth #ContentCreator #Automation #ProductivityTools
"""
    kit_path = os.path.join(CAMPAIGNS_DIR, "weekly_distribution_kit.md")
    with open(kit_path, "w", encoding="utf-8") as f:
        f.write(kit)
    return kit_path

def main():
    leads = load_leads()
    print("="*60)
    print("   🎯 CLIPPILOT CREATOR OUTREACH & GROWTH AGENT")
    print("="*60)
    print(f" Loaded Leads / Niches: {len(leads)}")
    for l in leads:
        print(f"  • [{l['id']}] {l['name']} ({l['channel_type']}) - {l['status']}")

    kit_file = generate_weekly_distribution_kit()
    print(f"\n[✓] Generated Weekly Viral Distribution Kit at:\n    {kit_file}")
    print("="*60)

if __name__ == "__main__":
    main()
