import os
import sys
import glob
import subprocess
from core.scanner import get_registered_assets, deep_scan
from core.telemetry import get_last_commit_data
from core.sync import get_sync_status

MATURITY_WEIGHTS = {
    "PROTOTYPE": 0.5,
    "ALPHA": 1.0,
    "BETA": 2.0,
    "STABLE": 3.0,
    "PROD": 3.0,
    "RELEASE": 3.0
}

class SynquorkOrchestrator:
    def __init__(self):
        self.assets    = get_registered_assets()
        self.user_shell = (
            "/usr/bin/fish"
            if os.path.exists("/usr/bin/fish")
            else os.environ.get("SHELL", "/bin/sh")
        )
        # NUEVO: Forzar cálculo e inyección de progresos en RAM al arrancar la app
        if "07" in self.assets:
            from pathlib import Path
            from core.sync import build_portfolio_dataset
            dummy_path = Path(self.assets["07"]["path"]) / "docs/data/projects.json"
            # Llama a build_portfolio_dataset para mutar el diccionario assets en RAM con los cálculos correctos
            _, _ = build_portfolio_dataset(self.assets, dummy_path)
            
        self.sync_msg = get_sync_status(self.assets)

# ──────────────────────────────────────────────────────────────────────
    def _inject_and_jump(self, path, title):
        """Cambia al directorio del activo y abre una sesión flow anidada sin romper el proceso padre."""
        os.chdir(path)
        os.environ["SYNQUORK_ENV"] = title

        # ── CASO 1: dentro de tmux (origen: TUI de Synquork) ──────────────
        if "TMUX" in os.environ:
            current_session = subprocess.check_output(
                ["tmux", "display-message", "-p", "#S"], text=True
            ).strip()

            session_name = f"flow_{os.path.basename(path)}"

            if subprocess.run(
                ["tmux", "has-session", "-t", session_name],
                capture_output=True
            ).returncode != 0:
                # Dimensiones del cliente actual
                cols = subprocess.check_output(["tput", "cols"],  text=True).strip()
                rows = subprocess.check_output(["tput", "lines"], text=True).strip()

                subprocess.run([
                    "tmux", "new-session", "-d",
                    "-s", session_name, "-c", path,
                    "-x", cols, "-y", rows
                ], check=True)

                # Registrar sesión padre donde flow-exit la leerá
                subprocess.run([
                    "tmux", "set-environment",
                    "-t", session_name,
                    "SYNQUORK_PARENT_SESSION", current_session
                ], check=True)

                # Layout estándar: 3 paneles (espeja flow.fish)
                subprocess.run([
                    "tmux", "split-window", "-h",
                    "-t", session_name, "-c", path, "-p", "36"
                ], check=True)
                subprocess.run([
                    "tmux", "split-window", "-v",
                    "-t", f"{session_name}:0.1", "-c", path, "-p", "50"
                ], check=True)

                # Activar venv y adjuntar carga de flow.fish en todos los paneles si existe
                venv_cmd = (
                    "if test -f .venv/bin/activate.fish; source .venv/bin/activate.fish; end; "
                    "if test -f flow.fish; source flow.fish; end"
                )
                panes = subprocess.check_output(
                    ["tmux", "list-panes", "-t", session_name, "-F", "#{pane_id}"],
                    text=True
                ).strip().splitlines()

                for pane_id in panes:
                    subprocess.run([
                        "tmux", "send-keys", "-t", pane_id,
                        f"{venv_cmd}; clear", "Enter"
                    ])

                # Abrir editor en panel 0
                p0         = panes[0]
                candidates = (
                    glob.glob(os.path.join(path, "*.py"))  +
                    glob.glob(os.path.join(path, "*.tex")) +
                    glob.glob(os.path.join(path, "*.md"))
                )
                editor_cmd = f"v {candidates[0]}" if candidates else "v ."
                subprocess.run(["tmux", "send-keys", "-t", p0, editor_cmd, "Enter"])

            # RETORNO LIMPIO: Saltamos a la sesión de trabajo. Al salir con 'flow exit',
            # Tmux nos devuelve aquí. Eliminamos la shell interactiva huérfana para evitar el Ctrl+C.
            subprocess.run(["tmux", "switch-client", "-t", session_name])
            
            # Forzamos una limpieza de terminal al regresar para sanar el buffer visual
            print("\033[H\033[J", end="")

        # ── CASO 2: fuera de tmux (arranque directo) ──────────────────────
        else:
            import shutil, time

            if shutil.which("tmux"):
                session_name = f"synquork_{int(time.time())}"
                banner_text = f"Estado: Dentro de Synquork ({title})"

                tmux_cmd = [
                    "tmux", "new-session", "-d", "-s", session_name, f"exec {self.user_shell}", ";",
                    # 1. Habilitamos la barra de estado
                    "set-option", "-t", session_name, "status", "on", ";",
                    # 2. La movemos a la parte superior (Sticky)
                    "set-option", "-t", session_name, "status-position", "top", ";",
                    # 3. Centramos el contenido de forma nativa
                    "set-option", "-t", session_name, "status-justify", "centre", ";",
                    # 4. Configuración de estilo (Fondo cian, texto negro/gris oscuro)
                    "set-option", "-t", session_name, "status-style", "bg=colour235,fg=colour250,bold", ";",
                    # 5. Formato del texto (Limpiamos los componentes por defecto de Tmux como el reloj/fecha)
                    "set-option", "-t", session_name, "status-left", "", ";",
                    "set-option", "-t", session_name, "status-right", "", ";",
                    "set-option", "-t", session_name, "status-left-length", "0", ";",
                    "set-option", "-t", session_name, "status-right-length", "0", ";",
                    # 6. Inyectamos tu título
                    "set-option", "-t", session_name, "window-status-current-format", banner_text, ";",
                    "attach-session", "-t", session_name
                ]
                
                subprocess.run(tmux_cmd)

    # ──────────────────────────────────────────────────────────────────────
    def inspect_asset(self, asset_id):
        asset = self.assets[asset_id]
        while True:
            print("\033[H\033[J", end="")
            status_info = asset.get('status', {})

            print(f"--- DETALLES DEL ACTIVO: {asset['title']} ---")
            print(f" ID:         {asset_id} | {asset.get('visibility')} | Tag: {asset.get('tags')}")
            print(f" Estado:     {status_info.get('activity', 'N/A')} | Madurez: {status_info.get('maturity', 'ALPHA')} ({status_info.get('progress_pct', 0)}%)")
            print(f" Versión:    v{status_info.get('version', '0.1.0')}")
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

            if sys.stdin.seekable():
                sys.stdin.flush()

            choice = input("\nAcción > ").strip().upper()

            if not choice or choice.startswith('\033') or choice.startswith('^['):
                continue

            if choice == 'G':
                self._inject_and_jump(asset['path'], asset['title'])
            elif choice == 'B':
                break

    # ──────────────────────────────────────────────────────────────────────
    def run_tui(self):
        while True:
            self.sync_msg = get_sync_status(self.assets)
            print("\033[H\033[J", end="")
            print(f"\n{'═'*73}")
            print(f"         SYNQUORK TUI - BERNARD LAB")
            print(f"  Estado: {self.sync_msg}")
            print(f"{'═'*73}")

            if not self.assets:
                print(" [!] No hay activos.")
            else:
                # 1. Preparamos una lista de activos con su timestamp para ordenar
                lista_ordenada = []
                for uid, data in self.assets.items():
                    tele = get_last_commit_data(data['path'])
                    lista_ordenada.append({
                        "uid": uid,
                        "data": data,
                        "tele": tele,
                        "ts": tele.get('timestamp', 0)
                    })

                # 2. Ordenamos: reverse=True pone el timestamp más alto (más nuevo) al principio
                lista_ordenada.sort(key=lambda x: x['ts'], reverse=True)

                # 3. Imprimimos la lista ya ordenada
                for item in lista_ordenada:
                    uid = item['uid']
                    tele = item['tele']
                    fecha = tele.get('commit_date', "01-Ene-2026 00:00")
                    msg_clean = tele.get('commit_msg', "⚠️ Sin registros")
                    titulo_raw = item['data'].get('title', "Sin título")
                    
                    msg_preview = msg_clean[:22].ljust(22)
                    titulo_preview = titulo_raw[:20].ljust(20)
                    print(f" [{uid}] {fecha} | {msg_preview} | {titulo_preview}")

            # Modifica el bloque visual de opciones de la TUI dentro de core/orchestrator.py print(f"{'═'*73}")
            print(" [S] Re-Scan    [L] Push Local    [P] Push to Cloud    [Q] Salir")
            print(f"{'═'*73}")

            choice = input("\nID o Comando > ").strip().upper()

            if choice == 'Q':
                break
            elif choice == 'L':
                print("\n📦 Compilando metadatos de laboratorios...")
                from core.sync import push_local
                success, msg = push_local(self.assets)
                print(f" {'✅' if success else '❌'} {msg}")
                input("\nPresiona Enter para continuar...")
            elif choice == 'P':
                print("\n🚀 Preparando despliegue cloud...")
                from core.sync import push_to_cloud
                success, msg = push_to_cloud(self.assets)
                print(f" {'✅' if success else '❌'} {msg}")
                input("\nPresiona Enter para continuar...")
            elif choice.startswith('G') and choice[1:] in self.assets:
                target = self.assets[choice[1:]]
                self._inject_and_jump(target['path'], target['title'])
            elif choice == 'S':
                print("\n🔍 Re-escaneando laboratorios...")
                self.assets   = deep_scan()
                self.sync_msg = get_sync_status(self.assets)
                input("\nScan completo. Enter para refrescar...")
            elif choice in self.assets:
                self.inspect_asset(choice)
