import os
import sys
from core.scanner import get_registered_assets, deep_scan
from core.telemetry import get_last_commit_info

class SynquorkOrchestrator:
    def __init__(self):
        self.assets = get_registered_assets()
        # Priorizamos fish como ingenieros electrónicos en Fedora
        self.user_shell = "/usr/bin/fish" if os.path.exists("/usr/bin/fish") else os.environ.get("SHELL", "/bin/sh")

    def _inject_and_jump(self, path, title):
        """Inyecta variables de entorno y muta el proceso al shell del proyecto."""
        print(f"\n🚀 Saltando a {title}...")
        env = os.environ.copy()
        env["SYNQUORK_NESTED"] = "true"
        env["SYNQUORK_PROJECT"] = title
        
        try:
            os.chdir(path)
            os.execvpe(self.user_shell, [self.user_shell], env)
        except Exception as e:
            print(f"❌ Error al saltar: {e}")
            input("Presiona Enter para continuar...")

    def inspect_asset(self, asset_id):
        asset = self.assets[asset_id]
        while True:
            print("\033[H\033[J", end="")

            # Solo es LAB si github_url existe pero es explícitamente None o nulo
            # Si tiene un string con una URL, es un proyecto público.
            url = asset.get('github_url')
            is_lab = " [INTERNAL LAB]" if url is None else ""
            
            status = asset.get('status', {})

            print(f"\n{'─'*60}")
            # Dentro de core/orchestrator.py -> inspect_asset()
            print(f" 📂 PROYECTO: {asset['title'].upper()}{is_lab}")
            if asset.get('lab_notice'):
                print(f" 📢 NOTICE:   \033[1;33m{asset['lab_notice']}\033[0m") # Amarillo
            print(f" 📍 ID:        {asset_id}")
            # ... resto del print
            print(f" 🏷️  STATUS:   {status.get('label', 'N/A')} ({status.get('state', 'unknown')})")
            print(f" 🛠️  STACK:    {', '.join(asset.get('stack', []))}")
            print(f" 📝 DESC:     {asset.get('description')}")
            print(f"{'─'*60}")
            
            # ... resto del código (telemetría y inputs)
            
            print("\n [G] Jump (Muta Proceso)  [B] Back")
            op = input("\n Selección > ").strip().lower()
            
            if op == 'g':
                self._inject_and_jump(asset['path'], asset['title'])
            elif op == 'b':
                break

    def run_tui(self):
        while True:
            print("\033[H\033[J", end="")
            print(f"\n{'═'*50}")
            print(f"        SYNKORK TUI - BERNARD LAB")
            print(f"{'═'*50}")
            
            if not self.assets:
                print(" [!] No hay activos. Usa [S] para escanear.")
            else:
                for uid, data in self.assets.items():
                    print(f" [{uid}] {data['title'].ljust(25)}")
            
            print(f"{'═'*50}")
            print(" [S] Deep Scan  [Q] Salir")
            print(f"{'═'*50}")
            
            choice = input("\nID o Comando > ").strip().upper()
            
            if choice == 'Q':
                break
            elif choice == 'S':
                print("\n🔍 Iniciando escaneo en ~/")
                self.assets = deep_scan()
                input("\nScan completo. Enter para refrescar...")
            elif choice in self.assets:
                self.inspect_asset(choice)
