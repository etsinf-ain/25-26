import spade
import asyncio
from spade import agent
from spade_bdi.bdi import BDIAgent

async def main():
    agent = BDIAgent("family@localhost", "1234", "family.asl")
    await agent.start()
    await asyncio.sleep(1)  # Wait for the agent to process the beliefs and rules
    agent.bdi.print_beliefs()
    await agent.stop()

if __name__ == "__main__":
    spade.run(main())