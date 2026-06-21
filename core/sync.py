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

def check_git_status(repo_path):
    """
    Retorna True si el repositorio tiene cambios locales sin guardar
    (untracked, modified, o staged), de lo contrario False.
    """
    try:
        # --porcelain da una salida limpia y estable ideal para scripts
        res = subprocess.check_output(
            ["git", "-C", str(repo_path), "status", "--porcelain"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        return len(res) > 0
    except Exception:
        return False

def get_sync_status(assets):
    """
    Función ligera para el header de la TUI.
    Verifica si el archivo projects.json existe, su antigüedad y alertas de Git.
    """
    if "07" not in assets:
        return "⚠️ Portafolio no registrado"

    portfolio_path = Path(assets["07"]["path"])
    dest_path = portfolio_path / "docs/data/projects.json"

    if not dest_path.exists():
        return "❌ Desincronizado (projects.json missing)"

    # NUEVO: Alerta temprana de código sin guardar en el Portafolio
    if check_git_status(portfolio_path):
        return "⚠️ ALERTA: Portafolio con cambios locales sin consolidar en Git"

    mtime = datetime.fromtimestamp(dest_path.stat().st_mtime, tz=timezone(timedelta(hours=-5)))
    return f"✅ Sincronizado ({mtime.strftime('%H:%M')} PET)"

def check_portfolio_sync(assets):
    """Verificación detallada para el modo inspección."""
    if "07" not in assets:
        return

    portfolio_path = Path(assets["07"]["path"])
    print(f"🔍 Validando integridad en: {portfolio_path}")
    
    try:
        # Obtenemos el listado detallado estilo porcelain
        status_raw = subprocess.check_output(
            ["git", "-C", str(portfolio_path), "status", "--porcelain"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        
        if status_raw:
            print("\n \033[1;33m⚠️ ADVERTENCIA: Tienes cambios locales sin guardar en el Portafolio:\033[0m")
            for line in status_raw.splitlines():
                print(f"   ↳ {line}")
            print(" \033[1;36m💡 Recomendación:\033[0m Haz 'git add' y 'git commit' en el portafolio antes de sincronizar.")
        else:
            print(" ✨ Git Working Tree: Limpio e impecable.")
            
    except Exception as e:
        print(f" ❌ No se pudo verificar el estado de Git: {e}")

# core/sync.py
# (Mantén tus imports y las funciones _generate_diff y get_sync_status intactas)

def build_portfolio_dataset(assets, dest_path):
    """Genera el diccionario estructurado v2 unificando assets y telemetría."""
    from core.telemetry import get_last_commit_data

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
        raw_repo = data.get("repository", {})
        raw_env = data.get("environment", {})

        entry = {
            "id": uid,
            "title": data.get("title"),
            "category": data.get("category"),
            "visibility": data.get("visibility", "PRIVATE"),
            "tags": data.get("tags", ""),
            "domain": data.get("domain", []),
            "status": {
                "activity": raw_status.get("activity", "ACTIVE"),
                "maturity": raw_status.get("maturity", "ALPHA"),
                "version": raw_status.get("version", "0.1.0"),
                "progress_pct": raw_status.get("progress_pct", 0),
                "scopes": raw_status.get("scopes", {})
            },
            "environment": {
                "os": raw_env.get("os", "Fedora 43"),
                "shell": raw_env.get("shell", "fish")
            },
            "repository": {
                "ssh": raw_repo.get("ssh", ""),
                "https": raw_repo.get("https", "")
            },
            "stack": data.get("stack", []),
            "description": data.get("description"),
            "_telemetry": {
                "last_update": git_data['time_str'].split(" // ")[0],
                "last_commit_log": git_data['commit_msg']
            }
        }
        project_map[uid] = entry

    now_pet = datetime.now(timezone(timedelta(hours=-5)))
    return {
        "metadata": {
            "owner": "Marcos Bernard",
            "global_status": "Operational",
            "last_sync": now_pet.strftime('%Y-%m-%d // %H:%M PET'),
            "operational_stack": existing_data.get("metadata", {}).get("operational_stack", {}),
            "stats": {"total_managed": len(project_map)}
        },
        "projects": sorted(list(project_map.values()), key=lambda x: x['id'])
    }, now_pet


def push_local(assets):
    """Fase 1: Construye, muestra DIFF y escribe el JSON localmente exponiendo rutas."""
    if "07" not in assets:
        return False, "Portafolio no hallado en el registro."

    portfolio_path = Path(assets["07"]["path"]).resolve()
    dest_path = (portfolio_path / "docs/data/projects.json").resolve()

    # Compilamos la estructura en memoria
    full_data, now_pet = build_portfolio_dataset(assets, dest_path)

    print("\n" + "="*60)
    print("🔬 MODO DEBUGGER: SEGUIMIENTO DE ESCRITURA LOCAL")
    print("="*60)
    print(f" 📂 Directorio raíz detectado : {portfolio_path}")
    print(f" 📝 Archivo objetivo de salida: {dest_path}")
    print(f" 📊 Cantidad de assets en RAM : {len(assets)} laboratorios")
    print("="*60)
    print("📋 INSPECCIÓN DE CAMBIOS LOCALES (DIFF)")
    print("="*60)
    
    # Esto te mostrará si hay cambios reales en los strings o solo formateo
    print(_generate_diff(dest_path, full_data))
    print("="*60)

    confirm = input("\n¿Aplicar cambios al archivo local projects.json? [s/N] > ").strip().lower()
    if confirm != 's':
        return False, "Operación local abortada."

    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, indent=2, ensure_ascii=False)
        
        return True, f"Modificación exitosa -> {dest_path.name} actualizado offline."
    except Exception as e:
        return False, f"Error crítico escribiendo en {dest_path}: {str(e)}"


def push_to_cloud(assets):
    """Fase 2: Realiza el ciclo Git sobre el estado actual del JSON."""
    if "07" not in assets:
        return False, "Portafolio no hallado en el registro."

    portfolio_path = Path(assets["07"]["path"])
    dest_path = portfolio_path / "docs/data/projects.json"

    if not dest_path.exists():
        return False, "No existe projects.json local. Corre [L] primero."

    confirm = input("\n¿Sincronizar y hacer push a GitHub? [s/N] > ").strip().lower()
    if confirm != 's':
        return False, "Push cancelado."

    now_pet = datetime.now(timezone(timedelta(hours=-5)))
    commit_msg = f"chore(sync): auto-update project states {now_pet.strftime('%H:%M')} PET"
    
    git_success, git_msg = _git_commit_and_push(portfolio_path, commit_msg)
    if git_success:
        return True, "Sincronización remota: GitHub OK."
    return False, f"Fallo en el Push: {git_msg}"


def _git_commit_and_push(repo_path, message):
    """Ejecuta el ciclo de Git: add, commit y push."""
    try:
        subprocess.run(["git", "-C", str(repo_path), "add", "docs/data/projects.json"], check=True)
        subprocess.run(["git", "-C", str(repo_path), "commit", "-m", message], check=True)
        subprocess.run(["git", "-C", str(repo_path), "push"], check=True)
        return True, "Cloud Update: Success"
    except subprocess.CalledProcessError as e:
        return False, f"Git Error: {e}"
