import json
from core.scanner import get_registered_assets, REGISTRY_PATH

class SynquorkOrchestrator:
    def __init__(self):
        # Cargamos los datos del registro
        self.assets = get_registered_assets()

    def list_assets(self):
        """Retorna una lista formateada."""
        return [(uid, data['title'], data['path']) for uid, data in self.assets.items()]

    def run_tui(self):
        """Interfaz de usuario básica."""
        print(f"\n{'='*45}")
        print(f"       SYNKORK TUI - BERNARD LAB")
        print(f"{'='*45}")
        
        assets = self.list_assets()
        if not assets:
            print(" [!] No hay activos registrados. Corre un deep scan.")
            return

        for uid, title, path in assets:
            print(f" [{uid}] {title.ljust(20)} | {path}")

        print(f"{'='*45}")
        choice = input("\n> Ingresa ID para inspeccionar (o 'q' para salir): ").strip()
        
        if choice in self.assets:
            print(f"\nSeleccionaste: {self.assets[choice]['title']}")
        elif choice.lower() != 'q':
            print(" [!] ID no válido.")

# El bloque de entrada debe estar fuera de la clase
if __name__ == "__main__":
    orch = SynquorkOrchestrator()
    orch.run_tui()
