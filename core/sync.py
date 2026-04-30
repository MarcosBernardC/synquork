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
