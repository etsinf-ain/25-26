import argparse
import spade
import asyncio
from spade_bdi.bdi import BDIAgent


def parse_args():
    parser = argparse.ArgumentParser(description="Run a BDI solver with a selected .asl file")
    parser.add_argument("rule_file", help="Path to the .asl file to execute")
    return parser.parse_args()


async def main(rule_file):
    bdi_agent = BDIAgent("solver@localhost", "1234", rule_file)
    await bdi_agent.start()
    await asyncio.sleep(3)  # Keep the agent running for a while to allow it to process
    await bdi_agent.stop()

if __name__ == "__main__":
    args = parse_args()
    spade.run(main(args.rule_file))