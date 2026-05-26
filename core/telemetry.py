# core/telemetry.py
import subprocess
from datetime import datetime, timedelta, timezone

def get_last_commit_data(repo_path):
    """
    Retorna metadatos de Git compatibles con el formato PET (UTC-5).
    Filtra commits automáticos de Synquork para evitar bucles de actualización.
    """
    try:
        # COMANDO REFINADO: Excluye los commits automatizados de sincronización
        cmd = [
            "git", "-C", repo_path, "log", "-1",
            "--grep=chore(sync)", "--invert-grep",
            "--format=%at|%s"
        ]

        result = subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL
        ).strip()

        if not result:
            # Si no queda nada tras el filtro, intenta obtener el último real sin filtros
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

        # --- FORMATEO MANUAL PARA EVITAR FALLOS DE LOCALE ---
        meses_es = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        mes_str = meses_es[dt_pet.month - 1]

        # Formato final exacto: 26-May-2026 08:03 (Ocupa 17 caracteres fijos)
        fecha_custom = f"{dt_pet.strftime('%d')}-{mes_str}-{dt_pet.year} {dt_pet.strftime('%H:%M')}"

        return {
            "timestamp": ts_unix,
            "time_str": time_str,
            "log": f"{dt_pet.strftime('%H:%M')} | {msg}",
            "commit_date": fecha_custom,
            "commit_msg": msg
        }
    except Exception:
        return {
            "timestamp": 0,
            "time_str": "2026-01-01 // 00:00 PET",
            "log": "⚠️ Sin registros de actividad",
            "commit_date": "01-Ene-2026 00:00",
            "commit_msg": "⚠️ Sin registros de actividad"
        }
