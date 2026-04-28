import os
import sys
import subprocess

# --- BOOTSTRAP ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.scanner import get_registered_assets, deep_scan
from core.telemetry import get_last_commit_info 

class SynquorkOrchestrator:
    def __init__(self):
        self.assets = get_registered_assets()
        self.user_shell = os.environ.get("SHELL", "/bin/sh")

    def _inject_and_jump(self, path, title):
        """Prepara el entorno y realiza la sustitución de proceso."""
        print(f"\n🚀 Saltando a {title}...")
        
        # 1. Preparar las variables de entorno
        # Copiamos el entorno actual y añadimos nuestra etiqueta
        env = os.environ.copy()
        env["SYNQUORK_NESTED"] = "true"
        env["SYNQUORK_PROJECT"] = title

        # 2. Cambiar directorio
        os.chdir(path)

        # 3. Informar al usuario sobre el estado del Shell
        print(f"💡 Info: Terminal vinculada a Synquork. Escribe 'exit' para cerrar panel.")
        
        # 4. MUTAR (os.execvpe permite pasar las nuevas variables de entorno)
        # Usamos execvpe para que el Shell reciba la variable SYNQUORK_NESTED
        os.execvpe(self.user_shell, [self.user_shell], env)

    def inspect_asset(self, asset_id):
        asset = self.assets[asset_id]
        path = asset['path']

        while True:
            print("\033[H\033[J", end="")
            print(f"\n{'─'*50}")
            print(f" 📂 PROYECTO: {asset['title'].upper()}")
            print(f" 📍 RUTA:     {path}")
            print(f"{'─'*50}")
            print("\n [G] Jump: MUTAR proceso y activar Label")
            print(" [B] Back: Volver")

            op = input("\n Selección > ").strip().lower()

            if op == 'g':
                self._inject_and_jump(path, asset['title'])

            if op == 'b':
                break

# ... (show_stats y run_tui se mantienen igual que en la versión anterior) ...
    def show_stats(self):
        print("\033[H\033[J", end="")
        print(f"\n{'═'*80}")
        print(f"        TELEMETRÍA DE ACTIVOS - ÚLTIMOS LOGS")
        print(f"{'═'*80}")
        
        # Cabecera de la tabla
        print(f" {'ID':<6} | {'PROYECTO':<15} | {'HASH':<8} | {'FECHA':<10} | {'LOG'}")
        print(f"{'─'*80}")

        for uid, data in self.assets.items():
            path = data['path']
            # Llamamos a la telemetría real
            info = get_last_commit_info(path)
            print(f" [{uid:<3}] | {data['title'][:15]:<15} | {info}")

        print(f"{'═'*80}")
        input("\nPresiona Enter para volver...")

    def run_tui(self):
        while True:
            print("\033[H\033[J", end="")
            print(f"\n{'═'*50}")
            print(f"        SYNKORK TUI - BERNARD LAB")
            print(f"{'═'*50}")

            for uid, data in self.assets.items():
                print(f" [{uid}] {data['title'].ljust(25)}")

            print(f"{'═'*50}")
            # Cambiamos la leyenda para reflejar el nuevo comando
            print(" [S] Deep Scan (Sync)  [T] Telemetry  [Q] Salir") 
            print(f"{'═'*50}")

            choice = input("\nID para gestionar > ").strip().upper()
            
            if choice == 'Q': 
                break
            elif choice == 'S': 
                # Ejecuta el escaneo físico y actualiza el diccionario en memoria
                print("\n🔍 Iniciando escaneo de laboratorios...")
                self.assets = deep_scan() 
                input("\nScan completo. Presiona Enter para refrescar lista...")
            elif choice == 'T': 
                # Movimos Telemetry a 'T' para liberar la 'S'
                self.show_stats()
            elif choice in self.assets: 
                self.inspect_asset(choice)


if __name__ == "__main__":
    orch = SynquorkOrchestrator()
    if len(sys.argv) > 1:
        target_id = sys.argv[1].upper()
        if target_id in orch.assets:
            orch._inject_and_jump(orch.assets[target_id]['path'], orch.assets[target_id]['title'])
    orch.run_tui()
