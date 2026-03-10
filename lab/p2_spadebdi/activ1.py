import spade
import asyncio
from spade_bdi.bdi import BDIAgent

async def main():
    porter = BDIAgent("porter@localhost", "1234", "porter.asl")
    paranoid = BDIAgent("paranoid@localhost","1234", "paranoid.asl")
    claust = BDIAgent("claustrophobic@localhost","1234", "claustrophobic.asl")
    
    # Start the agents
    await porter.start()
    await paranoid.start()
    await claust.start()    
    await asyncio.sleep(3)
    # Stop the agents
    await porter.stop()
    await paranoid.stop()
    await claust.stop()


if __name__ == "__main__":
    spade.run(main())