import spade
from spade import agent
from spade_bdi.bdi import BDIAgent

async def main():
    agent = BDIAgent("hello@localhost", "1234", "hello_world.asl")
    await agent.start()

if __name__ == "__main__":
    spade.run(main())