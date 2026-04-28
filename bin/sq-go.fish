function sq-go
    # 1. Ejecutar el orquestador
    python3 ~/dev/ActiveLabs/synquork/core/orchestrator.py

    # 2. Verificar si Python dejó una ruta de salto
    if test -f /tmp/sq_jump
        set -l target (cat /tmp/sq_jump)
        rm /tmp/sq_jump # Limpiar el rastro
        
        if test -d $target
            cd $target
            commandline -f repaint # Refrescar el prompt de Fish
            echo "🚀 Teletransportado a: "(set_color cyan)$target(set_color normal)
        else
            echo "⚠️ Error: La ruta ya no existe."
        end
    end
end
