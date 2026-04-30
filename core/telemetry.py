import subprocess
import os

def get_last_commit_info(repo_path):
    try:
        # El flag -C ejecuta git como si estuvieras dentro de repo_path
        result = subprocess.check_output(
            ["git", "-C", repo_path, "log", "-1", '--format=%h | %as | %s'],
            stderr=subprocess.STDOUT,
            text=True
        ).strip()
        return result
    except Exception:
        return "⚠️  No se detectaron commits o ruta inválida."
