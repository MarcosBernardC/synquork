#!/usr/bin/env python
import sys
import os

# Forzamos al intérprete a ver la raíz del proyecto
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.orchestrator import SynquorkOrchestrator

if __name__ == "__main__":
    orch = SynquorkOrchestrator()
    
    # Soporte para argumentos directos: sq-menu 01
    if len(sys.argv) > 1:
        target_id = sys.argv[1].upper()
        if target_id in orch.assets:
            asset = orch.assets[target_id]
            orch._inject_and_jump(asset['path'], asset['title'])
        else:
            print(f"❌ ID [{target_id}] no encontrado.")
            sys.exit(1)
    
    orch.run_tui()
