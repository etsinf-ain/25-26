import os
import sys
import matplotlib.pyplot as plt
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sim_engine import SumoEngine

def main():
    if len(sys.argv) < 2:
        print("Uso: uv run test_engine.py <modelo.sumocfg> [semilla]")
        sys.exit(1)

    cfg_file = sys.argv[1]
    if not os.path.exists(cfg_file):
        print(f"Error: No se encuentra el archivo {cfg_file}")
        sys.exit(1)

    seed = int(sys.argv[2]) if len(sys.argv) > 2 else random.randint(0, 999999)
    
    print(f"Modelo: {cfg_file}")
    print(f"Semilla: {seed}")

    engine = SumoEngine(cfg_file, seed=seed)
    
    try:
        engine.start()
        plt.ion()
        fig, ax = plt.subplots(figsize=(8, 8))
        engine.setup_viz(ax)

        while True:
            try:
                sim_time, veh_count = engine.update_viz(ax)
                ax.set_title(f"Modelo: {cfg_file} | Tiempo: {sim_time}s | Semilla: {seed}")
                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.02)
            except Exception:
                break
                
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
    finally:
        engine.close()
        plt.close('all')

if __name__ == "__main__":
    main()
