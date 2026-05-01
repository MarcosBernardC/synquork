# core/sync.py
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

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
        return False, "Portafolio no hallado."

    dest_path = Path(assets["07"]["path"]) / "docs/data/projects.json"
    from core.telemetry import get_last_commit_data

    full_data = {
        "metadata": {
            "owner": "Marcos Bernard",
            "global_status": "Operational",
            "last_sync": datetime.now(timezone(timedelta(hours=-5))).strftime('%Y-%m-%d // %H:%M PET'),
            "operational_stack": {
                "core": ["C", "XC8 Specialist", "Python 3.14 (struct, toml)", "ASM"],
                "eda_cad": ["KiCad", "FreeCAD (Python Scripting)"],
                "env": ["Fedora 43", "Hyprland", "NVIM", "Tmux", "Fish", "Yazi"],
                "docs": ["LuaLaTeX", "XeLaTeX", "Zathura"]
            },
            "stats": {}
        },
        "projects": []
    }

    for uid, data in assets.items():
        git_data = get_last_commit_data(data['path'])

        entry = {
            "id": uid,
            "title": data.get("title"),
            "category": data.get("category"),
            "domain": data.get("domain", []),
            "status": data.get("status"), 
            "environment": {
                "os": data.get("environment", {}).get("os", "Fedora 43"),
                "shell": "fish",
                "last_update": git_data['time_str']
            },
            "github_url": data.get("github_url"),
            "stack": data.get("stack", []),
            "description": data.get("description")
        }
        full_data["projects"].append(entry)

    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, indent=2, ensure_ascii=False)
        return True, "Handshake exitoso: projects.json actualizado en PET."
    except Exception as e:
        return False, f"Error de escritura: {str(e)}"
