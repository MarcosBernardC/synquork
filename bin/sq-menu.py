# core/orchestrator.py (Añade este método al final)

def run_tui(self):
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
        self.inspect_asset(choice)
    elif choice.lower() != 'q':
        print(" [!] ID no válido.")

def inspect_asset(self, asset_id):
    asset = self.assets[asset_id]
    print(f"\n--- Detalle: {asset['title']} ---")
    print(f"Ruta: {asset['path']}")
    # Aquí es donde luego añadiremos Git status, uptime, etc.
    input("\nPresiona Enter para volver...")
