import subprocess
import os

def get_last_commit_info(repo_path):
    """Extrae el hash corto, la fecha y el mensaje del último commit."""
    try:
        # Comando: git log -1 --format="%h | %as | %s"
        # %h: hash corto, %as: fecha short (YYYY-MM-DD), %s: mensaje
        result = subprocess.check_output(
            ["git", "-C", repo_path, "log", "-1", '--format=%h | %as | %s'],
            stderr=subprocess.STDOUT,
            text=True
        ).strip()
        return result
    except Exception:
        return "Sin commits o no es un repo Git"
