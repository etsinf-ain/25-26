import SumoNetVis
import matplotlib.pyplot as plt
import os

def main():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    net_path = os.path.join(BASE_DIR, "scenarios", "dayuan", "dayuan.net.xml")
    if os.path.exists(net_path):
        net = SumoNetVis.Net(net_path)
        net.plot()
        plt.show()
    else:
        print(f"Error: Network file not found at {net_path}")

if __name__ == "__main__":
    main()
