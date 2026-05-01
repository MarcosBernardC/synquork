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
        """Cambia el directorio y lanza una nueva instancia de Fish."""
        print(f"\n🚀 Saltando a: {title}...")
        os.chdir(path)
        # Usamos execvp para que Synquork sea reemplazado por la shell en ese path
        os.execvp(self.user_shell, [self.user_shell])

    def inspect_asset(self, asset_id):
        asset = self.assets[asset_id]
        while True:
            print("\033[H\033[J", end="")
            print(f"--- DETALLES DEL ACTIVO: {asset['title']} ---")
            print(f" Categoría: {asset['category']}")
            print(f" Ruta:      {asset['path']}")
            print(f" Stack:     {', '.join(asset['stack'])}")

            if asset_id == "07":
                from core.sync import check_portfolio_sync
                check_portfolio_sync(self.assets)

            last_log = get_last_commit_info(asset['path'])
            print(f" 🕒 ÚLTIMO LOG: \033[1;32m{last_log}\033[0m")

            print(f"\n{'─'*50}")
            print(" [G] Go (Abrir Terminal)   [B] Volver")
            print(f"{'─'*50}")

            choice = input("\nAcción > ").strip().upper()

            if choice == 'G':
                self._inject_and_jump(asset['path'], asset['title'])
            elif choice == 'B':
                break

    def run_tui(self):
        while True:
            # Forzamos la actualización del estado en cada refresco de pantalla
            self.sync_msg = get_sync_status(self.assets)
            
            print("\033[H\033[J", end="")
            print(f"\n{'═'*55}")
            print(f"         SYNKORK TUI - BERNARD LAB")
            print(f"  Estado: {self.sync_msg}")
            print(f"{'═'*55}")
            
            # ... (resto de la TUI)
            
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
            elif choice.startswith('G') and choice[1:] in self.assets:
                target = self.assets[choice[1:]]
                self._inject_and_jump(target['path'], target['title'])
            elif choice == 'S':
                print("\n🔍 Re-escaneando laboratorios...")
                self.assets = deep_scan()
                self.sync_msg = get_sync_status(self.assets) # Actualiza estado tras scan
                input("\nScan completo. Enter para refrescar...")
            elif choice in self.assets:
                self.inspect_asset(choice)
