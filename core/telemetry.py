# core/telemetry.py
import subprocess
from datetime import datetime, timedelta, timezone

def get_last_commit_data(repo_path):
    """
    Retorna metadatos de Git compatibles con el nuevo formato PET // UTC-5.
    Mantiene el nombre para no romper el Orquestador.
    """
    try:
        # Obtenemos timestamp UNIX (%at) y el mensaje corto (%s)
        result = subprocess.check_output(
            ["git", "-C", repo_path, "log", "-1", "--format=%at|%s"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()

        ts_unix_str, msg = result.split('|')
        ts_unix = int(ts_unix_str)

        # Ajuste a PET (UTC-5)
        tz_pet = timezone(timedelta(hours=-5))
        dt_pet = datetime.fromtimestamp(ts_unix, tz=tz_pet)

        # Formato para la TUI y el JSON: 2026-04-30 // 20:20 PET
        time_str = dt_pet.strftime('%Y-%m-%d // %H:%M PET')

        return {
            "timestamp": ts_unix,
            "time_str": time_str,
            "log": f"{dt_pet.strftime('%H:%M')} | {msg}"
        }
    except Exception:
        return {
            "timestamp": 0, 
            "time_str": "2026-01-01 // 00:00 PET", 
            "log": "⚠️ Sin commits"
        }

