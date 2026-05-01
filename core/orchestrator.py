import os
import sys
from core.scanner import get_registered_assets, deep_scan
from core.telemetry import get_last_commit_data
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

            tele = get_last_commit_data(asset['path'])
            print(f" 🕒 ÚLTIMO LOG: \033[1;32m{tele['log']}\033[0m")

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
            self.sync_msg = get_sync_status(self.assets)
            print("\033[H\033[J", end="")
            print(f"\n{'═'*65}")
            print(f"          SYNKORK TUI - BERNARD LAB")
            print(f"  Estado: {self.sync_msg}")
            print(f"{'═'*65}")

            if not self.assets:
                print(" [!] No hay activos.")
            else:
                for uid, data in self.assets.items():
                    # Obtener telemetría fresca para el listado
                    tele = get_last_commit_data(data['path'])
                    # Mostramos solo la parte del log que tiene la fecha/hora
                    log_preview = tele['log'][:30]
                    print(f" [{uid}] {log_preview.ljust(32)} | {data['title']}")

            print(f"{'═'*65}")
            print(" [S] Re-Scan    [P] Push to Cloud    [Q] Salir")
            print(f"{'═'*65}")

            choice = input("\nID o Comando > ").strip().upper()

            if choice == 'Q': break
            elif choice == 'P':
                print("\n🚀 Sincronizando metadatos con el Portafolio...")
                from core.sync import push_local_to_portfolio
                success, msg = push_local_to_portfolio(self.assets)
                if success:
                    print(f" ✅ {msg}")
                else:
                    print(f" ❌ {msg}")
                input("\nPresiona Enter para continuar...")
            # ... resto de la lógica (G, S, ID)
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
