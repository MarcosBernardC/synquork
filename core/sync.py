import json
from pathlib import Path

def check_portfolio_sync(assets):
    """Compara el registro de Synquork con el JSON del Portafolio."""
    
    # 1. Localizar el Portafolio mediante el ID 07 en el registro de Synquork
    if "07" not in assets:
        return "❌ Error: Portafolio 2026 no está en el registro local."

    portfolio_path = Path(assets["07"]["path"]) / "docs/data/projects.json"
    
    if not portfolio_path.exists():
        return f"⚠️ No se encontró el archivo en: {portfolio_path}"

    try:
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            portfolio_data = json.load(f)
            # Asumiendo que el JSON tiene una llave "projects" o es una lista directa
            # Ajustamos según tu estructura:
            remote_projects = portfolio_data if isinstance(portfolio_data, list) else portfolio_data.get("projects", [])
    except Exception as e:
        return f"❌ Error leyendo projects.json: {e}"

    # 2. Encontrar intersección de IDs
    local_ids = set(assets.keys())
    remote_ids = {str(p.get("id")).zfill(2) for p in remote_projects}
    
    common_ids = local_ids.intersection(remote_ids)
    
    # 3. Mostrar resultados
    print(f"\n🔍 [SYNC CHECK] Proyectos encontrados en ambos sistemas:")
    print(f"{'─'*50}")
    if not common_ids:
        print(" No hay proyectos en común todavía.")
    else:
        for uid in sorted(common_ids):
            titulo = assets[uid]['title']
            print(f" ✅ ID {uid} | {titulo.ljust(20)} | [Sincronizado]")
    print(f"{'─'*50}")
    print(f" Total en común: {len(common_ids)}")

def get_sync_status(assets):
    """Devuelve un estado optimista: Verde si Local está respaldado en Cloud."""
    local_count = len(assets)
    
    if "07" not in assets:
        return f"\033[1;31mLocal: {local_count} | Cloud: -- | Handshake: ❌\033[0m"

    portfolio_path = Path(assets["07"]["path"]) / "docs/data/projects.json"
    if not portfolio_path.exists():
        return f"\033[1;33mLocal: {local_count} | Cloud: ?? | Handshake: ⚠️\033[0m"

    try:
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            remote_projects = data if isinstance(data, list) else data.get("projects", [])
            
            cloud_count = len(remote_projects)
            local_ids = set(assets.keys())
            remote_ids = {str(p.get("id")).zfill(2) for p in remote_projects}
            handshake_count = len(local_ids.intersection(remote_ids))
            
            # Lógica optimista: Verde si lo local está contenido en la nube
            if handshake_count >= local_count:
                color = "\033[1;32m" # Verde: "Todo lo local está a salvo"
            else:
                color = "\033[1;33m" # Amarillo: "Falta subir algo local"
                
            return f"{color}Local: {local_count} | Cloud: {cloud_count} | Handshake: {handshake_count}\033[0m"
    except:
        return f"\033[1;31mLocal: {local_count} | Cloud: ERROR | Handshake: ❌\033[0m"
