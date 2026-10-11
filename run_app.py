"""
VinZie Budget Tracker - Browser Launcher Script
Runs the Flask application and automatically launches your default web browser.
"""

import os
import sys
import time
import webbrowser
import threading
from app import create_app

def open_browser(url: str):
    """Wait for server to start, then open the browser window."""
    time.sleep(1.2)
    print(f"\n[LAUNCHER] Opening web browser at: {url}\n")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[LAUNCHER] Could not auto-launch browser ({e}). Please manually open {url}")

def main():
    # Ensure database exists before launching
    db_file = os.path.join(os.path.dirname(__file__), "database", "finance.db")
    if not os.path.exists(db_file):
        print("[LAUNCHER] Database not found. Running initialization and seeding...")
        import init_db
        init_db.init_database()

    port = int(os.getenv("PORT", 5000))
    app_url = f"http://127.0.0.1:{port}"

    # Launch browser in a background daemon thread
    browser_thread = threading.Thread(target=open_browser, args=(app_url,), daemon=True)
    browser_thread.start()

    print("=" * 65)
    print("  VINZIE BUDGET TRACKER")
    print(f"  Status     : Server starting on {app_url}")
    print(f"  Browser    : Opening automatically in your default browser...")
    print(f"  Demo Login : demo_user  |  Password: DemoPass@123")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 65)

    app = create_app("development")
    # use_reloader=False avoids duplicate browser opening from Werkzeug process watcher
    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=False)

if __name__ == "__main__":
    main()
