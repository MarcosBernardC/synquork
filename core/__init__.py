if __name__ == "__main__":
    orch = SynquorkOrchestrator()
    
    # VENTAXA: Salto directo si pasas el ID como argumento
    if len(sys.argv) > 1:
        target_id = sys.argv[1].upper()
        if target_id in orch.assets:
            path = orch.assets[target_id]['path']
            os.chdir(path)
            os.execvp("fish", ["fish"]) # Sustitución inmediata
        else:
            print(f"❌ ID [{target_id}] no encontrado.")
            sys.exit(1)
            
    # Si no hay argumentos, abre la TUI normal
    orch.run_tui()
