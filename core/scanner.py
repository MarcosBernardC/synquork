import os
import json
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent.parent / "config" / "registry.json"

def deep_scan(root_dir="~/"):
    """Busca físicamente todos los repositorios con meta.json."""
    found_assets = {}
    search_path = Path(root_dir).expanduser().resolve()
    
    print(f"🔍 Iniciando Deep Scan en {search_path}...")
    
    for root, dirs, files in os.walk(str(search_path)):
        # Si encontramos .git y meta.json, es un acierto
        if ".git" in dirs and "meta.json" in files:
            try:
                with open(os.path.join(root, "meta.json"), 'r') as f:
                    data = json.load(f)
                    asset_id = data.get("id")
                    if asset_id:
                        found_assets[asset_id] = {
                            "path": root,
                            "title": data.get("title")
                        }
                # No necesitamos entrar en subcarpetas de un repo ya hallado
                dirs.clear() 
            except Exception as e:
                print(f"⚠️ Error en {root}: {e}")
                
    # Persistir en el registro
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(found_assets, f, indent=4)
    
    return found_assets

def get_registered_assets():
    """Carga rápida desde el archivo de registro."""
    if not REGISTRY_PATH.exists():
        return deep_scan() # Si no hay registro, hacemos uno
        
    with open(REGISTRY_PATH, 'r') as f:
        return json.load(f)
