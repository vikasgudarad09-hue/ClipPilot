"""
ClipPilot Autonomous Agent Suite - Unified Control Center
Connects all automation agents: 3D Video Production, Growth Outreach, and Desktop Studio.
"""
import os
import sys
import json
import subprocess
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    print("""
================================================================
   ✈️   C L I P P I L O T   A U T O N O M O U S   S U I T E  🇮🇳
   Autonomous 3D Video Production & Creator Growth Engine
================================================================
 Live Website : https://clippilot-studio.web.app
 Checkout URL : https://clippilot-studio.web.app/checkout.html
 Creator / Dev: Vikas Prabhu Gudarad
================================================================
""")

def run_3d_pipeline():
    print("\n[+] Starting Autonomous 3D Video Production Pipeline...")
    print("    This will run Blender 5.2 in background, compile with FFmpeg,")
    print("    generate Multilingual AI SEO, and queue videos into ClipPilot.\n")
    confirm = input("Press ENTER to start rendering (or 'q' to cancel): ")
    if confirm.lower() == 'q':
        return
    subprocess.run([sys.executable, "auto_render_pipeline.py"], cwd=BASE_DIR)
    input("\nPress ENTER to return to menu...")

def run_growth_agent():
    print("\n[+] Running Creator Outreach & Viral Distribution Agent...")
    subprocess.run([sys.executable, "growth_agent.py"], cwd=BASE_DIR)
    kit_path = os.path.join(BASE_DIR, "campaigns", "weekly_distribution_kit.md")
    if os.path.exists(kit_path):
        print(f"\n[✓] Distribution Kit generated at:\n    {kit_path}")
        open_kit = input("\nWould you like to open the kit now? (y/n): ")
        if open_kit.lower() == 'y':
            os.system(f'notepad "{kit_path}"')
    input("\nPress ENTER to return to menu...")

def launch_clippilot_studio():
    print("\n[+] Launching ClipPilot Studio Desktop Application...")
    studio_dir = os.path.join(BASE_DIR, "OmniPost_Studio")
    subprocess.Popen([sys.executable, "app.py"], cwd=studio_dir)
    print("[✓] ClipPilot launched! Check your browser window at http://127.0.0.1:8765")
    input("\nPress ENTER to return to menu...")

def generate_customer_license():
    print("\n[+] Customer License Key Generator")
    email = input("Enter customer email or order reference: ").strip()
    if not email:
        print("[!] Email cannot be empty.")
        return
    studio_dir = os.path.join(BASE_DIR, "OmniPost_Studio")
    subprocess.run([sys.executable, "generate_key.py", email], cwd=studio_dir)
    input("\nPress ENTER to return to menu...")

def view_queue_status():
    queue_path = os.path.join(BASE_DIR, "OmniPost_Studio", "data", "queue.json")
    print("\n[+] Current ClipPilot Publishing Queue:")
    if not os.path.exists(queue_path):
        print("    [!] Queue is empty. No videos added yet.")
    else:
        try:
            with open(queue_path, "r", encoding="utf-8") as f:
                queue = json.load(f)
            if not queue:
                print("    [!] Queue is empty.")
            else:
                for idx, item in enumerate(queue, 1):
                    sched = item.get("scheduled_time_human") or "Not scheduled yet"
                    print(f"    {idx}. {item.get('title')} ({item.get('file_name')})")
                    print(f"       Status: {item.get('status')} | Schedule: {sched}\n")
        except Exception as e:
            print(f"    [!] Error reading queue: {e}")
    input("\nPress ENTER to return to menu...")

def open_links():
    print("\n[+] Opening Live Website & Checkout in Browser...")
    webbrowser.open("https://clippilot-studio.web.app")
    webbrowser.open("https://clippilot-studio.web.app/checkout.html")
    input("\nPress ENTER to return to menu...")

def main():
    while True:
        clear_screen()
        print_banner()
        print(" [1] 🎬 Auto-Produce 3D Videos (Blender ➔ FFmpeg ➔ AI SEO ➔ Queue)")
        print(" [2] 🎯 Run Creator Outreach & Generate Viral Distribution Kit")
        print(" [3] 🚀 Launch ClipPilot Studio Desktop App")
        print(" [4] 📊 View Current Video Publishing Queue")
        print(" [5] 🔑 Generate Pro License Key (for paying customers)")
        print(" [6] 🌐 Open Live Website & Checkout Page")
        print(" [0] ❌ Exit")
        print("="*64)

        choice = input("Enter choice (0-6): ").strip()
        if choice == "1":
            run_3d_pipeline()
        elif choice == "2":
            run_growth_agent()
        elif choice == "3":
            launch_clippilot_studio()
        elif choice == "4":
            view_queue_status()
        elif choice == "5":
            generate_customer_license()
        elif choice == "6":
            open_links()
        elif choice == "0":
            print("\nExiting ClipPilot Suite. Keep building!\n")
            break
        else:
            print("[!] Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
