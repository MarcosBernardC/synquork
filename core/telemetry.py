import subprocess

def get_last_commit_info(repo_path):
    try:
        # Añadimos timeout para evitar bloqueos por cortes de energía o discos lentos
        result = subprocess.check_output(
            ["git", "-C", repo_path, "log", "-1", '--format=%h | %as | %s'],
            stderr=subprocess.STDOUT,
            text=True,
            timeout=2  # <--- Crucial
        ).strip()
        return result
    except subprocess.TimeoutExpired:
        return "⏳ Timeout: Git no responde."
    except Exception:
        return "⚠️  No se detectaron commits o ruta inválida."
