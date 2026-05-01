import subprocess
from datetime import datetime

def get_last_commit_data(repo_path):
    """Retorna un diccionario con el timestamp y el log formateado con hora."""
    try:
        # %at: timestamp UNIX
        # %ad: fecha formateada con --date
        result = subprocess.check_output(
            ["git", "-C", repo_path, "log", "-1", '--date=format:%H:%M', '--format=%at|%ad | %h | %s'],
            stderr=subprocess.STDOUT, text=True, timeout=2
        ).strip()

        parts = result.split('|', 1)
        return {
            "timestamp": int(parts[0]),
            "log": parts[1]
        }
    except Exception:
        return {"timestamp": 0, "log": "⚠️  Sin commits"}
