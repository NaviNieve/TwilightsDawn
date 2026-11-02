import json
import threading
import urllib3
from ui.dark_update_modal import show_dark_update_popup

GITHUB_AUTHOR = "NaviNieve"
GITHUB_REPO = "TwilightsDawn"

def check_for_updates_async(root_window, current_version):
    """Launches the update scanner inside an isolated worker background thread."""
    worker = threading.Thread(target=execute_version_check_sieve, args=(root_window, current_version), daemon=True)
    worker.start()


def execute_version_check_sieve(root_window, current_version):
    """Queries the GitHub REST API using the hardened urllib3 socket pool system."""
    url = f"https://api.github.com/repos/{GITHUB_AUTHOR}/{GITHUB_REPO}/releases/latest"

    try:
        http = urllib3.PoolManager(timeout=4.0, retries=False)

        response = http.request(
            'GET',
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )

        if response.status == 200:
            data = json.loads(response.data.decode('utf-8'))
            latest_tag = data.get("tag_name", "").strip()
            html_url = data.get("html_url", f"https://github.com/repos/{GITHUB_AUTHOR}/{GITHUB_REPO}/releases")

            if latest_tag and latest_tag != current_version:
                root_window.after(0, lambda: show_dark_update_popup(root_window, latest_tag, html_url))
                root_window.after(0, lambda: root_window.inject_dynamic_update_alert_link(html_url))

    except Exception as err:
        print(f"[-] Network Exception Trapped inside Engine loop: {err}")