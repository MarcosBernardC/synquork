# core/telemetry.py
import subprocess
from datetime import datetime, timedelta, timezone

def get_last_commit_data(repo_path):
    """
    Retorna metadatos de Git compatibles con el formato PET (UTC-5).
    Filtra commits automáticos de Synquork para evitar bucles de actualización.
    """
    try:
        # COMANDO REFINADO:
        # --grep="chore(sync)": busca el patrón de tus commits automáticos
        # --invert-grep: EXCLUYE los que coincidan con ese patrón
        # De esta forma, siempre obtenemos el último commit "humano"
        cmd = [
            "git", "-C", repo_path, "log", "-1", 
            "--grep=chore(sync)", "--invert-grep", 
            "--format=%at|%s"
        ]
        
        result = subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL
        ).strip()

        if not result:
            # Si después de filtrar no queda nada (repo virgen o solo commits de sync)
            # intentamos obtener el último commit sin filtros para no devolver error
            result = subprocess.check_output(
                ["git", "-C", repo_path, "log", "-1", "--format=%at|%s"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()

        ts_unix_str, msg = result.split('|', 1)
        ts_unix = int(ts_unix_str)

        # Configuración de zona horaria PET (Perú Time / UTC-5)
        tz_pet = timezone(timedelta(hours=-5))
        dt_pet = datetime.fromtimestamp(ts_unix, tz=tz_pet)

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
            "log": "⚠️ Sin registros de actividad"
        }
