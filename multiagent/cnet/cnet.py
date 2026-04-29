import asyncio
import spade
from spade_bdi.bdi import BDIAgent

async def main():
    # list of agents
    # 1 initiator, 3 participants, 1 rejecting proposal
    agents = []
    agents.append(BDIAgent("init@localhost", "1234", "initiator.asl"))
    agents.append(BDIAgent("part1@localhost", "1234", "participant.asl"))
    agents.append(BDIAgent("part2@localhost", "1234", "participant.asl"))
    agents.append(BDIAgent("part3@localhost", "1234", "participant.asl"))
    agents.append(BDIAgent("reject@localhost", "1234", "reject.asl"))

    print("Start agents")
    for agent in agents:
        await agent.start()

    await asyncio.sleep(15)
    print("Finished. Stop agents")
    for agent in agents:
        print(f"** {agent.jid} beliefs")
        # add source=True to print the source of the beliefs
        # agent.bdi.print_beliefs(source=True)
        agent.bdi.print_beliefs()
        await agent.stop()
    print("Agents stopped")

if __name__ == "__main__":
    spade.run(main())