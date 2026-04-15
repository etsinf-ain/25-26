import asyncio
import spade
import agentspeak
from spade_bdi.bdi import BDIAgent


class RobotArmAgent(BDIAgent):
    def add_custom_actions(self, actions):
        @actions.add(".move", 2)
        def _m_move(agent, term, intention):
            src = agentspeak.grounded(term.args[0], intention.scope)
            dest = agentspeak.grounded(term.args[1], intention.scope)
            print("put", src,"on", dest)
            yield 


async def main():
    robotarm = RobotArmAgent("robotarm@localhost", "1234", "blocks.asl")
    await robotarm.start()

    await asyncio.sleep(1)
    print("**final beliefs")
    robotarm.bdi.print_beliefs()
    await robotarm.stop()



if __name__ == "__main__":
    spade.run(main())