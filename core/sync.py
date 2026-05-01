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
    """Devuelve un mensaje corto del estado de sincronización."""
    if "07" not in assets:
        return "\033[1;31mNo sincronizado (Falta ID 07)\033[0m"
    
    portfolio_path = Path(assets["07"]["path"]) / "docs/data/projects.json"
    if not portfolio_path.exists():
        return "\033[1;33mNo sincronizado (JSON ausente)\033[0m"
    
    try:
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            remote_count = len(data if isinstance(data, list) else data.get("projects", []))
            return f"\033[1;32mSincronizado al Portafolio ({remote_count} proyectos)\033[0m"
    except:
        return "\033[1;31mError de sincronización\033[0m"
