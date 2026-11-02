import urllib.request
import json
import threading

GITHUB_AUTHOR = "NaviNieve"
GITHUB_REPO = "TwilightsDawn"

def check_for_updates_async(root_window, current_version):
    """Launches the update scanner inside an isolated worker background thread."""
    worker = threading.Thread(target=execute_version_check_sieve, args=(root_window, current_version), daemon=True)
    worker.start()

def execute_version_check_sieve(root_window, current_version):
    """Queries the GitHub REST API securely using passed version parameters."""
    url = f"https://github.com/{GITHUB_AUTHOR}/{GITHUB_REPO}/releases/latest"
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                latest_tag = data.get("tag_name", "").strip()
                html_url = data.get("html_url", f"https://github.com/{GITHUB_AUTHOR}/{GITHUB_REPO}/releases")

                if latest_tag and latest_tag != current_version:
                    root_window.after(0, lambda: show_dark_update_popup(root_window, latest_tag, html_url))
                    root_window.after(0, lambda: root_window.inject_dynamic_update_alert_link(html_url))

    except Exception as e:
        print(f"[UPDATER] Update check bypassed (Offline or repo private): {e}")