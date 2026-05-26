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
        """Cambia el directorio, abre Fish y maneja un banner del tamaño mínimo absoluto."""
        os.chdir(path)
        
        os.environ["SYNQUORK_ENV"] = title
        # Quitamos el emoji inicial para ahorrar espacio horizontal si la terminal es pequeña
        banner_text = f" Estado: Dentro de Synquork ({title}) "

        # Caso 1: YA ESTÁS DENTRO DE TMUX
        if "TMUX" in os.environ:
            import subprocess
            
            current_pane = os.environ.get("TMUX_PANE", "")
            
            # CAMBIO CLAVE: Usa "-l 1" para forzar a que el panel mida EXACTAMENTE 1 línea de alto.
            # Usamos "echo -n" para evitar que el salto de línea genere scroll o espacios vacíos.
            tmux_split_cmd = [
                "tmux", "split-window", "-vb", "-t", current_pane, "-l", "1", "-P", "-F", "#{pane_id}",
                f"echo -n -e '\\033[1;30;46m{banner_text:^50}\\033[0m'; tail -f /dev/null"
            ]
            
            # Ejecutamos la división y capturamos el ID del banner
            result = subprocess.run(tmux_split_cmd, capture_output=True, text=True)
            banner_pane_id = result.stdout.strip()
            
            # Aseguramos el foco de vuelta en tu panel de trabajo
            subprocess.run(["tmux", "select-pane", "-t", current_pane])
            
            # Lanzamos tu Fish Shell operativa
            subprocess.run([self.user_shell])
            
            # Al salir con exit, eliminamos el banner de 1 línea instantáneamente
            subprocess.run(["tmux", "kill-pane", "-t", banner_pane_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Caso 2: ESTÁS FUERA DE TMUX
        else:
            import shutil
            if shutil.which("tmux"):
                import time
                session_name = f"synquork_{int(time.time())}"
                # Aquí también aplicamos "-l 1" para mantener la consistencia
                tmux_cmd = [
                    "tmux", "new-session", "-d", "-s", session_name, f"exec {self.user_shell}", ";",
                    "split-window", "-vb", "-t", session_name, "-l", "1", f"echo -n -e '\\033[1;30;46m{banner_text:^50}\\033[0m'; tail -f /dev/null", ";",
                    "set-option", "-t", session_name, "status", "off", ";",
                    "select-pane", "-t", f"{session_name}:0.1", ";",
                    "attach-session", "-t", session_name
                ]
                os.execvp("tmux", tmux_cmd)
            else:
                banner_cmd = f"echo -e '\\n\\033[1;36m[ Estado: Dentro de Synquork ({title}) ]\\033[0m\\n'"
                os.execvp(self.user_shell, [self.user_shell, "-C", banner_cmd])

    def inspect_asset(self, asset_id):
        asset = self.assets[asset_id]
        while True:
            print("\033[H\033[J", end="")
            status_info = asset.get('status', {})
            
            print(f"--- DETALLES DEL ACTIVO: {asset['title']} ---")
            print(f" ID:         {asset_id} | {asset.get('visibility')}")
            print(f" Estado:     {status_info.get('state')} ({status_info.get('label')})")
            print(f" Categoría:  {asset['category']}")
            print(f" Stack:      {', '.join(asset['stack'])}")

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
            print(f"          SYNQUORK TUI - BERNARD LAB")
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
