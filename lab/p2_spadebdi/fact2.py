import spade
import asyncio
from spade_bdi.bdi import BDIAgent

async def main():
    fact = BDIAgent("fact@localhost", "1234", "fact2.asl")
    await fact.start()
    await asyncio.sleep(1)
    fact.bdi.print_beliefs()
    await fact.stop()

if __name__ == "__main__":
    spade.run(main())