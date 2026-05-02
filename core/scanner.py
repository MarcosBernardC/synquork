import os
import json
from pathlib import Path

# Definimos la ruta del registro persistente
REGISTRY_PATH = Path(__file__).parent.parent / "config" / "registry.json"

def get_registered_assets():
    """Carga rápida del registro o escaneo inicial si no existe."""
    if not REGISTRY_PATH.exists():
        return deep_scan()
    try:
        with open(REGISTRY_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return deep_scan()

def deep_scan(root_dir="~/"):
    """
    Busca exhaustivamente repositorios que contengan .git Y meta.json.
    """
    found_assets = {}
    # Expandimos el home del usuario Bernard
    search_path = Path(root_dir).expanduser().resolve()
    
    # Directorios que SÍ o SÍ debemos ignorar para no entrar en bucles o carpetas de sistema
    # Eliminamos '.git' de la lista de exclusión para que os.walk pueda entrar y verlo
    BLACKLIST = {
        'node_modules', 'venv', '.venv', '__pycache__', 
        '.local', '.cache', '.mozilla', '.config', '.var'
    }

    print(f"🔍 Escaneando laboratorios en: {search_path}...")

    for root, dirs, files in os.walk(str(search_path), topdown=True):
        # Modificamos dirs in-place para ignorar la basura y optimizar
        dirs[:] = [d for d in dirs if d not in BLACKLIST]

        # CRITERIO DE DETECCIÓN:
        # 1. Debe existir una carpeta .git
        # 2. Debe existir un archivo meta.json
        if ".git" in dirs and "meta.json" in files:
            meta_path = os.path.join(root, "meta.json")
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    asset_id = str(data.get("id")).zfill(2)

                    if asset_id:
                        found_assets[asset_id] = {
                            "path": root,
                            "title": data.get("title", os.path.basename(root)),
                            "category": data.get("category", "N/A"),
                            "visibility": data.get("visibility", "PRIVATE"),  # Nuevo
                            "domain": data.get("domain", []),
                            "status": data.get("status", {}),                 # Captura el objeto anidado
                            "environment": data.get("environment", {}),       # Captura el objeto anidado
                            "links": data.get("links", {}),                   # Captura el objeto anidado
                            "stack": data.get("stack", []),
                            "description": data.get("description", "Sin descripción.")
                        }
                        print(f" ✅ Activo hallado: {found_assets[asset_id]['title']} [{asset_id}]")
                
                # Una vez encontrado un proyecto, no escaneamos sus subcarpetas
                dirs.clear() 
                
            except Exception as e:
                print(f" ⚠️ Error leyendo meta en {root}: {e}")

    # Persistencia
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(found_assets, f, indent=4)

    print(f"\n✨ Escaneo finalizado. Total de activos: {len(found_assets)}")
    return found_assets
