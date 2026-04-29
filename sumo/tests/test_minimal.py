import traci
import matplotlib.pyplot as plt
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg_path = os.path.join(BASE_DIR, "scenarios", "dayuan", "dayuan.sumocfg")

traci.start(["sumo", "-c", cfg_path])

plt.ion()
fig, ax = plt.subplots()

for step in range(500):
    traci.simulationStep()

    ax.clear()

    xs, ys = [], []

    for v in traci.vehicle.getIDList():
        x, y = traci.vehicle.getPosition(v)
        xs.append(x)
        ys.append(y)

    ax.scatter(xs, ys)
    ax.set_title(f"Step {step}")

    plt.pause(0.05)

traci.close()
plt.ioff()
plt.show()