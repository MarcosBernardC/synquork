import os
import sys
from core.scanner import get_registered_assets, deep_scan
from core.telemetry import get_last_commit_info
from core.sync import get_sync_status  # Nueva función ligera

class SynquorkOrchestrator:
    def __init__(self):
        # 1. Carga o Escaneo inicial
        self.assets = get_registered_assets()
        self.user_shell = "/usr/bin/fish" if os.path.exists("/usr/bin/fish") else os.environ.get("SHELL", "/bin/sh")
        
        # 2. Verificación de sincronización minimalista al iniciar
        self.sync_msg = get_sync_status(self.assets)

    def _inject_and_jump(self, path, title):
        # ... (se mantiene igual)
        pass

    def inspect_asset(self, asset_id):
        asset = self.assets[asset_id]
        while True:
            print("\033[H\033[J", end="")
            # ... (Lógica de impresión de metadata)
            print(f"--- DETALLES DEL ACTIVO: {asset['title']} ---")
            print(f" Categoría: {asset['category']}")
            print(f" Ruta: {asset['path']}")

            # El handshake detallado se queda aquí solo como información extendida
            if asset_id == "07":
                from core.sync import check_portfolio_sync
                check_portfolio_sync(self.assets)

            last_log = get_last_commit_info(asset['path'])
            print(f" 🕒 ÚLTIMO LOG: \033[1;32m{last_log}\033[0m")

            # MANTENER ESTO DENTRO DEL WHILE
            print(f"\n{'─'*50}")
            print(" [B] Volver al menú principal")
            print(f"{'─'*50}")

            choice = input("\nAcción > ").strip().upper()

            if choice == 'B':
                break  # Ahora sí está dentro del bucle

    def run_tui(self):
        while True:
            print("\033[H\033[J", end="")
            print(f"\n{'═'*50}")
            print(f"        SYNKORK TUI - BERNARD LAB")
            # Mensaje minimalista de estado de sincronización
            print(f"        Estado: {self.sync_msg}") 
            print(f"{'═'*50}")
            
            if not self.assets:
                print(" [!] No hay activos. Usa [S] para escanear.")
            else:
                for uid, data in self.assets.items():
                    print(f" [{uid}] {data['title'].ljust(25)}")
            
            print(f"{'═'*50}")
            print(" [S] Re-Scan    [Q] Salir")
            print(f"{'═'*50}")
            
            choice = input("\nID o Comando > ").strip().upper()
            
            if choice == 'Q': break
            elif choice == 'S':
                print("\n🔍 Re-escaneando laboratorios...")
                self.assets = deep_scan()
                self.sync_msg = get_sync_status(self.assets) # Actualiza estado tras scan
                input("\nScan completo. Enter para refrescar...")
            elif choice in self.assets:
                self.inspect_asset(choice)
