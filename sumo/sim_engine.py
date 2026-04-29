import traci
import sumolib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import sys
import re

class SumoEngine:
    """
    Core simulation engine that wraps the SUMO TraCI API.
    
    Manages network loading (sumolib), simulation startup
    (supporting Multi-Client mode for Agents), and synchronization
    with Matplotlib visualization.
    """
    def __init__(self, cfg_file, seed=None):
        """
        Initializes the simulation engine.
        
        Args:
            cfg_file (str): Path to the SUMO configuration file (.sumocfg).
            seed (int, optional): Seed to ensure reproducibility.
        """
        self.cfg_file = cfg_file
        self.seed = seed
        self.net_file = self._get_net_file_from_cfg(self.cfg_file)
        self.net = sumolib.net.readNet(self.net_file)
        self.tl_markers = []
        self.step_count = 0
        
    def _get_net_file_from_cfg(self, cfg_file):
        """Extracts the .net.xml path dynamically from the .sumocfg file."""
        with open(cfg_file, 'r') as f:
            content = f.read()
            match = re.search(r'net-file value="([^"]+)"', content)
            if match: 
                net_rel = match.group(1)
                cfg_dir = os.path.dirname(cfg_file)
                if cfg_dir:
                    return os.path.join(cfg_dir, net_rel)
                return net_rel
        return None

    def start(self, wait_for_agents=False, port=8813):
        """
        Starts the SUMO process via TraCI.
        
        Args:
            wait_for_agents (bool): If True, activates Multi-Client mode.
                The simulator will wait for an external agent connection.
            port (int): TraCI port to use if wait_for_agents is True.
        """
        cmd = ["sumo", "-c", self.cfg_file, "--no-step-log", "--no-warnings"]
        if self.seed is not None:
            cmd.extend(["--seed", str(self.seed)])
            
        if wait_for_agents:
            # TraCI Multi-client: SUMO will wait for the Agent to connect.
            # By setting num-clients to 2, the simulation requires both clients to be connected.
            cmd.extend(["--num-clients", "2"])
            traci.start(cmd, port=port)
            # traci.setOrder(1) sets this script (Dashboard) as Client 1.
            # Client 1 advances time, but SUMO will block advancement until
            # Client 2 (Agent, Order=2) finishes sending its commands and processes its step.
            traci.setOrder(1)
        else:
            traci.start(cmd)

    def setup_viz(self, ax):
        """
        Sets up the initial network visualization in Matplotlib.
        Draws the road edges and initializes the traffic light markers.
        """
        for edge in self.net.getEdges():
            for lane in edge.getLanes():
                shape = lane.getShape()
                ax.plot([p[0] for p in shape], [p[1] for p in shape], color="gray", linewidth=1, zorder=1)
        
        self.tl_markers = []
        for tl_id in traci.trafficlight.getIDList():
            lanes = traci.trafficlight.getControlledLanes(tl_id)
            unique_lanes = {}
            for i, lane_id in enumerate(lanes):
                if lane_id not in unique_lanes: unique_lanes[lane_id] = []
                unique_lanes[lane_id].append(i)
            
            for lane_id, indices in unique_lanes.items():
                lane = self.net.getLane(lane_id)
                pos = lane.getShape()[-1]
                marker = ax.scatter(pos[0], pos[1], s=40, color="red", zorder=4, edgecolors="black", linewidth=0.5)
                self.tl_markers.append({"tl_id": tl_id, "indices": indices, "marker": marker})

        # Defines the space where the simulation will take place as a scatter plot
        self.v_dots = ax.scatter([], [], color="blue", s=15, zorder=3)
        xmin, ymin, xmax, ymax = self.net.getBoundary()
        ax.set_xlim(xmin-10, xmax+10); ax.set_ylim(ymin-10, ymax+10)
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])

    def get_step_data(self):
        """
        Advances the simulation by one step and collects the current state data.
        
        Returns:
            dict: Dictionary with step information:
                - time (float): Current simulation time.
                - veh_count (int): Number of vehicles in the network.
                - positions (list): List of tuples (x, y) with vehicle positions.
                - tl_states (dict): Mapping {traffic_light_id: "traci_state_string"}.
        """
        traci.simulationStep()
        veh_ids = traci.vehicle.getIDList()
        positions = [traci.vehicle.getPosition(v) for v in veh_ids]
        tl_states = {tid: traci.trafficlight.getRedYellowGreenState(tid) for tid in traci.trafficlight.getIDList()}
        return {"time": traci.simulation.getTime(), "veh_count": len(veh_ids), "positions": positions, "tl_states": tl_states}

    def update_viz(self, ax, data=None):
        """
        Updates the Matplotlib plot with the new step data.
        Refreshes vehicle positions and traffic light colors.
        """
        if data is None: data = self.get_step_data()
        self.step_count += 1
        if data["positions"]: self.v_dots.set_offsets(data["positions"])
        else: self.v_dots.set_offsets(np.empty((0, 2)))
        for m in self.tl_markers:
            state = data["tl_states"][m["tl_id"]]
            chars = [state[i] for i in m["indices"]]
            # Logic adapted to Spain - Visualization priorities:
            # 1. 'y' / 'Y' -> Transition phase to red (orange)
            # 2. 'g' -> Unprotected green / Yield (yellow) -> Overrides 'G'
            # 3. 'G' -> Protected green (lime)
            # 4. 'r' / 'R' -> Red (red)
            if 'y' in chars or 'Y' in chars: color = "orange"
            elif 'g' in chars: 
                # Blinking yellow (amber intermitente) every step
                color = "orange" if self.step_count % 2 == 0 else "dimgray" 

            elif 'G' in chars: color = "lime"
            else: color = "red"
            
            m["marker"].set_facecolor(color)
        return data["time"], data["veh_count"]

    def close(self):
        """Safely closes the TraCI connection."""
        try: traci.close()
        except: pass
