import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time
import random
import os
import sys
import numpy as np
import glob

# Import the simulation engine
from sim_engine import SumoEngine

st.set_page_config(page_title="SUMO Dashboard", layout="centered")

# Persistent configuration to keep the simulation engine alive between reruns
if 'engine' not in st.session_state:
    st.session_state.engine = None
if 'running' not in st.session_state:
    st.session_state.running = False    

st.sidebar.title("Simulation Control")

# Get all configuration files in the scenarios directory
cfg_files = sorted(glob.glob('scenarios/*/*.sumocfg'))

def format_cfg_name(path):
    """Utility to show only the scenario folder name in the selectbox."""
    return os.path.basename(os.path.dirname(path)).capitalize()

selected_cfg = st.sidebar.selectbox("Scenario", cfg_files, format_func=format_cfg_name, disabled=st.session_state.running)
seed_input = st.sidebar.text_input("Seed", "", disabled=st.session_state.running)
wait_agents = st.sidebar.checkbox("Enable External Connection (Agents)", value=False, disabled=st.session_state.running)
agent_port = st.sidebar.number_input("Agent Port", value=8813, disabled=st.session_state.running)

# Speed control
speed_options = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
speed_factor = st.sidebar.select_slider(
    "Speed (1.0x = Real Time)",
    options=speed_options,
    value=1.0
)

col1, col2 = st.sidebar.columns(2)
start_btn = col1.button("▶️ Start")
stop_btn = col2.button("⏹️ Stop")

st.title("SUMO Control Center")

# STOP logic
if stop_btn:
    if st.session_state.engine:
        st.session_state.engine.close()
    st.session_state.engine = None
    st.session_state.running = False
    st.rerun()

# START logic
if start_btn and not st.session_state.running:
    # Use provided seed or generate a random one
    seed = int(seed_input) if seed_input.strip() else random.randint(0, 999999)
    
    # Regenerate the environment automatically using the seed if it's a procedural scenario
    if selected_cfg.endswith("random.sumocfg"):
        from tools import build_random_city
        build_random_city.create_random_city(seed)
    elif selected_cfg.endswith("autonomous.sumocfg"):
        from tools import build_autonomous_city
        build_autonomous_city.create_autonomous_city(seed)
    elif selected_cfg.endswith("interurban.sumocfg"):
        from tools import build_interurban
        build_interurban.create_interurban_network(seed)
    
    # Initialize and start the engine
    st.session_state.engine = SumoEngine(selected_cfg, seed=seed)
    if wait_agents:
        status_placeholder = st.sidebar.empty()
        status_placeholder.info(f"Waiting for agent on port {agent_port}...")
    
    st.session_state.engine.start(wait_for_agents=wait_agents, port=agent_port)
    
    if wait_agents:
        status_placeholder.empty()
    st.session_state.running = True
    st.session_state.seed = seed

# MAIN LOOP (Visualizer)
if st.session_state.running and st.session_state.engine:
    st.sidebar.code(f"Seed: {st.session_state.seed}")
    if wait_agents:
        st.sidebar.success(f"MAS detected at port {agent_port}")
    
    # Setup Figure and Axis
    fig, ax = plt.subplots(figsize=(6, 6))
    st.session_state.engine.setup_viz(ax)
    
    # Adjust traffic lights to be smaller for better visibility
    for m in st.session_state.engine.tl_markers:
        m["marker"].set_sizes([25])
    
    # Hide the default dots and use Rectangle patches for realistic vehicle drawing
    if hasattr(st.session_state.engine, "v_dots"):
        st.session_state.engine.v_dots.set_alpha(0)
    
    veh_patches = {}
    plot_placeholder = st.empty()
    
    try:
        import traci
        while st.session_state.running:
            start_time = time.time()
            data = st.session_state.engine.get_step_data()
            
            # Car patch management (Drawing cars as realistic boxes)
            veh_ids = traci.vehicle.getIDList()
            
            # Remove patches for vehicles that have left the simulation
            for vid in list(veh_patches.keys()):
                if vid not in veh_ids:
                    veh_patches[vid].remove()
                    del veh_patches[vid]
            
            # Draw/Update each car
            for vid in veh_ids:
                x, y = traci.vehicle.getPosition(vid)
                angle = traci.vehicle.getAngle(vid)
                plt_angle = -angle + 90
                
                if vid not in veh_patches:
                    r = patches.Rectangle((0,0), 5, 2, color="blue", zorder=3)
                    veh_patches[vid] = r
                    ax.add_patch(r)
                
                rad = np.radians(plt_angle)
                offset_x = 2.5 * np.cos(rad) - 1.0 * np.sin(rad)
                offset_y = 2.5 * np.sin(rad) + 1.0 * np.cos(rad)
                
                veh_patches[vid].set_xy((x - offset_x, y - offset_y))
                veh_patches[vid].angle = plt_angle
            
            # Update the underlying engine viz (for Traffic Lights)
            st.session_state.engine.update_viz(ax, data)
            
            # UI Updates
            ax.set_title(f"Time: {data['time']}s | Vehicles: {data['veh_count']} | {speed_factor}x")
            plot_placeholder.pyplot(fig, width="stretch")
            
            # Wait to maintain the requested simulation speed
            execution_time = time.time() - start_time
            wait_time = (1.0 / speed_factor) - execution_time
            if wait_time > 0: 
                time.sleep(wait_time)
            
    except Exception as e:
        st.error(f"Error en el bucle de simulación: {e}")
        st.session_state.running = False
    finally:
        if not st.session_state.running:
            st.success("Simulation finished.")
else:
    st.info("Configure the model and click Start.")
