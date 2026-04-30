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

# Persistent configuration
if 'engine' not in st.session_state:
    st.session_state.engine = None
if 'running' not in st.session_state:
    st.session_state.running = False    

st.sidebar.title("Simulation Control")

# Get all configuration files
cfg_files = sorted(glob.glob('scenarios/*/*.sumocfg'))

def format_cfg_name(path):
    return os.path.basename(os.path.dirname(path)).capitalize()

selected_cfg = st.sidebar.selectbox("Scenario", cfg_files, format_func=format_cfg_name, disabled=st.session_state.running)
seed_input = st.sidebar.text_input("Seed", "", disabled=st.session_state.running)
wait_agents = st.sidebar.checkbox("Enable External Connection (Agents)", value=False, disabled=st.session_state.running)
agent_port = st.sidebar.number_input("Agent Port", value=8813, disabled=st.session_state.running)

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

if stop_btn:
    if st.session_state.engine:
        st.session_state.engine.close()
    st.session_state.engine = None
    st.session_state.running = False
    st.rerun()

if start_btn and not st.session_state.running:
    seed = int(seed_input) if seed_input.strip() else random.randint(0, 999999)
    try: import traci; traci.close()
    except: pass
    
    # Regenerate the environment automatically using the seed
    # Lazy imports to avoid performance issues when loading the dashboard
    if selected_cfg.endswith("random.sumocfg"):
        from tools import build_random_city
        build_random_city.create_random_city(seed)
    elif selected_cfg.endswith("autonomous.sumocfg"):
        from tools import build_autonomous_city
        build_autonomous_city.create_autonomous_city(seed)
    elif selected_cfg.endswith("interurban.sumocfg"):
        from tools import build_interurban
        build_interurban.create_interurban_network(seed)
    elif selected_cfg.endswith("graph.sumocfg"):
        from tools import build_graph_network
        build_graph_network.create_sumo_graph_network(seed=seed)
    
    # Placeholder for state messages at sidebar
    st.session_state.engine = SumoEngine(selected_cfg, seed=seed)
    if wait_agents:
        status_placeholder = st.sidebar.empty()
        status_placeholder.info(f"Waiting for agent on port {agent_port}...")
    st.session_state.engine.start(wait_for_agents=wait_agents, port=agent_port)
    if wait_agents:
        status_placeholder.empty()
    st.session_state.running = True
    st.session_state.seed = seed

if st.session_state.running and st.session_state.engine:
    st.sidebar.code(f"Seed: {st.session_state.seed}")
    if wait_agents:
        st.sidebar.success(f"MAS detected at port {agent_port}")
    
    fig, ax = plt.subplots(figsize=(6, 6))
    st.session_state.engine.setup_viz(ax)
    
    # Adjust traffic lights to be smaller
    for m in st.session_state.engine.tl_markers:
        m["marker"].set_sizes([25])
    
    # Hide the points and prepare the rectangles
    if hasattr(st.session_state.engine, "v_dots"):
        st.session_state.engine.v_dots.set_alpha(0)
    
    veh_patches = getattr(st.session_state, "veh_patches", {})
    st.session_state.veh_patches = veh_patches
    
    plot_placeholder = st.empty()
    
    try:
        import traci
        while st.session_state.running:
            start_time = time.time()
            data = st.session_state.engine.get_step_data()
            
            # Car patch management
            veh_ids = traci.vehicle.getIDList()
            
            # Remove those that have left
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
                    # Cars are represented as rectangles of 5x2m
                    r = patches.Rectangle((0,0), 5, 2, color="blue", zorder=3)
                    veh_patches[vid] = r
                    ax.add_patch(r)
                
                # Update car position and rotation compensating the center
                rad = np.radians(plt_angle)
                offset_x = 2.5 * np.cos(rad) - 1.0 * np.sin(rad)
                offset_y = 2.5 * np.sin(rad) + 1.0 * np.cos(rad)
                
                veh_patches[vid].set_xy((x - offset_x, y - offset_y))
                veh_patches[vid].angle = plt_angle
            
            st.session_state.engine.update_viz(ax, data)
            ax.set_title(f"Time: {data['time']}s | Vehicles: {data['veh_count']} | {speed_factor}x")
            plot_placeholder.pyplot(fig, width="stretch")
            
            # Wait for the next step
            wait_time = (1.0 / speed_factor) - (time.time() - start_time)
            if wait_time > 0: time.sleep(wait_time)
            
    except Exception as e:
        st.session_state.running = False
    finally:
        st.success("Simulation finished.")
else:
    st.info("Configure the model and click Start.")
