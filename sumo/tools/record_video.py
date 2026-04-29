"""
record_video.py
Takes a SUMO configuration file and records a 300-step simulation video.
Saves the result as an MP4 animation inside the 'assets/' folder.
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import random
import os
from sim_engine import SumoEngine

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run tools/record_video.py <model.sumocfg> [seed]")
        sys.exit(1)

    cfg_file = sys.argv[1]
    if not os.path.exists(cfg_file):
        print(f"Error: Configuration file {cfg_file} not found.")
        sys.exit(1)

    seed = int(sys.argv[2]) if len(sys.argv) > 2 else random.randint(0, 999999)
    
    print(f"Recording {cfg_file} with SEED: {seed}")

    engine = SumoEngine(cfg_file, seed=seed)
    
    try:
        engine.start()
        plt.switch_backend('Agg')
        fig, ax = plt.subplots(figsize=(8, 8))
        engine.setup_viz(ax)

        writer = animation.FFMpegWriter(fps=20, bitrate=1800)
        os.makedirs("assets", exist_ok=True)
        base_name = os.path.basename(cfg_file).replace(".sumocfg", "").replace(".cfg", "")
        output_file = os.path.join("assets", f"{base_name}.mp4")
        
        with writer.saving(fig, output_file, dpi=100):
            for step in range(300):
                sim_time, veh_count = engine.update_viz(ax)
                ax.set_title(f"Model: {cfg_file} | Time: {sim_time}s | Seed: {seed}")
                writer.grab_frame()
                if step % 50 == 0:
                    print(f"Recording step {step}...")

        print(f"Video saved to {output_file}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        engine.close()

if __name__ == "__main__":
    main()
