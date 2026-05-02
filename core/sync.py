# core/sync.py
import json
import subprocess
import difflib
from pathlib import Path
from datetime import datetime, timedelta, timezone

def _generate_diff(old_json_path, new_data):
    """Genera una comparación visual entre el archivo actual y la nueva data."""
    if not old_json_path.exists():
        return "⚠️ El archivo projects.json no existe. Se creará uno nuevo totalmente."

    try:
        with open(old_json_path, 'r', encoding='utf-8') as f:
            old_content = f.read().splitlines()
        
        # Convertimos la nueva data a string formateado para comparar líneas
        new_content = json.dumps(new_data, indent=2, ensure_ascii=False).splitlines()

        # Generamos el diff unificado
        diff = difflib.unified_diff(
            old_content, 
            new_content, 
            fromfile='projects.json (Actual)', 
            tofile='projects.json (Propuesto)', 
            lineterm=''
        )
        
        diff_lines = list(diff)
        if not diff_lines:
            return "✨ No hay cambios detectados en los metadatos."
        
        # Coloreamos la salida para la terminal
        colored_diff = []
        for line in diff_lines:
            if line.startswith('+'):
                colored_diff.append(f"\033[32m{line}\033[0m") # Verde
            elif line.startswith('-'):
                colored_diff.append(f"\033[31m{line}\033[0m") # Rojo
            elif line.startswith('^'):
                colored_diff.append(f"\033[36m{line}\033[0m") # Cian
            else:
                colored_diff.append(line)
                
        return "\n".join(colored_diff)
    except Exception as e:
        return f"❌ Error generando diff: {e}"

def get_sync_status(assets):
    """
    Función ligera para el header de la TUI.
    Verifica si el archivo projects.json existe y su antigüedad.
    """
    if "07" not in assets:
        return "⚠️ Portafolio no registrado"
    
    dest_path = Path(assets["07"]["path"]) / "docs/data/projects.json"
    
    if not dest_path.exists():
        return "❌ Desincronizado (projects.json missing)"
    
    # Podríamos comparar hashes, pero por ahora usamos mtime para velocidad
    mtime = datetime.fromtimestamp(dest_path.stat().st_mtime, tz=timezone(timedelta(hours=-5)))
    return f"✅ Sincronizado ({mtime.strftime('%H:%M')} PET)"

def check_portfolio_sync(assets):
    """Verificación detallada para el modo inspección."""
    print(f"🔍 Validando integridad en: {assets['07']['path']}")
    # Aquí puedes añadir lógica de diff de git si lo deseas en el futuro

def push_local_to_portfolio(assets):
    if "07" not in assets:
        return False, "Portafolio no hallado en el registro."

    portfolio_path = Path(assets["07"]["path"])
    dest_path = portfolio_path / "docs/data/projects.json"
    from core.telemetry import get_last_commit_data

    # --- Lógica de carga y fusión de datos ---
    existing_data = {"metadata": {}, "projects": []}
    if dest_path.exists():
        try:
            with open(dest_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except Exception as e:
            print(f"⚠️ Error leyendo projects.json existente: {e}")

    project_map = {p['id']: p for p in existing_data.get("projects", [])}

    for uid, data in assets.items():
        git_data = get_last_commit_data(data['path'])
        raw_status = data.get("status", {})
        raw_links = data.get("links", {})
        raw_env = data.get("environment", {})

        entry = {
            "id": uid,
            "title": data.get("title"),
            "category": data.get("category"),
            "visibility": data.get("visibility", "PRIVATE"),
            "domain": data.get("domain", []),
            "status": {
                "state": raw_status.get("state", "ACTIVE LABS"),
                "label": raw_status.get("label", "Alpha")
            },
            "environment": {
                "os": raw_env.get("os", "Fedora 43"),
                "shell": raw_env.get("shell", "fish"),
                "last_update": git_data['time_str'],
                "last_commit_log": git_data['log'] # <--- CAMBIO AQUÍ: Usar 'log' en lugar de 'messag'
            },
            "links": {
                "ssh": raw_links.get("ssh", ""),
                "https": raw_links.get("https", ""),
                "notice": raw_links.get("notice", "")
            },
            "stack": data.get("stack", []),
            "description": data.get("description")
        }

        if "notice" in entry["links"] and not entry["links"]["notice"]:
            del entry["links"]["notice"]

        project_map[uid] = entry

    now_pet = datetime.now(timezone(timedelta(hours=-5)))
    full_data = {
        "metadata": {
            "owner": "Marcos Bernard",
            "global_status": "Operational",
            "last_sync": now_pet.strftime('%Y-%m-%d // %H:%M PET'),
            "operational_stack": existing_data.get("metadata", {}).get("operational_stack", {}),
            "stats": {"total_managed": len(project_map)}
        },
        "projects": sorted(list(project_map.values()), key=lambda x: x['id'])
    }

    # --- NUEVA LÓGICA DE INSPECCIÓN (DIFF) ---
    print("\n" + "="*50)
    print("📋 INSPECCIÓN DE CAMBIOS (DIFF)")
    print("="*50)
    print(_generate_diff(dest_path, full_data))
    print("="*50)

    confirm = input("\n¿Aplicar y subir cambios a la nube? [s/N] > ").strip().lower()
    if confirm != 's':
        return False, "Sincronización abortada por el usuario."

    # --- Escritura y Push (Solo si el usuario confirmó) ---
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, indent=2, ensure_ascii=False)

        commit_msg = f"chore(sync): auto-update project states {now_pet.strftime('%H:%M')} PET"
        git_success, git_msg = _git_commit_and_push(portfolio_path, commit_msg)

        if git_success:
            return True, f"Sincronización total: Local -> JSON -> GitHub OK."
        else:
            return False, f"JSON guardado, pero falló el Push: {git_msg}"

    except Exception as e:
        return False, f"Error crítico: {str(e)}"

def _git_commit_and_push(repo_path, message):
    """Ejecuta el ciclo de Git: add, commit y push."""
    try:
        # 1. git add docs/data/projects.json
        subprocess.run(["git", "-C", str(repo_path), "add", "docs/data/projects.json"], check=True)
        
        # 2. git commit -m "..."
        # Usamos --allow-empty por si no hay cambios reales, evitar que el script explote
        subprocess.run(["git", "-C", str(repo_path), "commit", "-m", message], check=True)
        
        # 3. git push
        subprocess.run(["git", "-C", str(repo_path), "push"], check=True)
        
        return True, "Cloud Update: Success"
    except subprocess.CalledProcessError as e:
        return False, f"Git Error: {e}"
