import asyncio
import spade
import random
import time
import agentspeak
from spade_bdi.bdi import BDIAgent

       
class RobotAgent(BDIAgent):
    def set_stock(self, N):
        self.N = N
        if N > 0:
            self.bdi.set_belief('available','beer','fridge')
        print("initial stock set")
   
    def set_owner(self, owner):
        self.owner = owner
        print("owner set")

    def add_custom_actions(self, actions):
        # open fridge and perceive stock
        @actions.add(".open", 1)
        def _m_open(agent, term, intention):
            print("[robot] opening fridge")
            self.bdi.set_belief("stock", self.N)
            yield
        
        @actions.add(".get", 1)
        def _m_get(agent, term, intention):
            # updates stock and stock belief
            # self.bdi.remove_belief("stock", "beer", self.N)
            if self.N == 0:
                print("[robot] no beer left")
                self.bdi.set_belief("stock", "beer", 0)    
                return
            self.N -= 1
            print("[robot] getting a beer", str(self.N),"left")
            self.bdi.set_belief("stock", "beer", self.N)
            yield

        @actions.add(".close", 1)
        def _m_close(agent, term, intention):
            print("[robot] closing fridge")
            self.bdi.remove_belief("stock", "beer", self.N)
            yield

        @actions.add(".hand_in", 1)
        def _m_hand_in(agent, term, intention):
            print("[robot] give the beer to owner")
            self.owner.bdi.set_belief("has", "owner", "beer")
            yield

        @actions.add(".move_towards", 1)
        def _m_move_towards(agent, term, intention):
            args = agentspeak.grounded(term.args, intention.scope)
            print("[robot] moving towards", args[0])
            #remove current position belief
            #current_pos = self.bdi.get_belief_value("at")
            #if current_pos != None:
            #    self.bdi.remove_belief("at")
            self.bdi.set_belief("at", "robot", args[0])
            yield

        @actions.add(".restock", 1)
        def _m_restock(agent, term, intention):
            args = agentspeak.grounded(term.args, intention.scope)
            qty = int(args[0])
            self.N += qty
            print("[robot] fridge restocked:", self.N, "beers")
            yield


class OwnerAgent(BDIAgent):
    def add_custom_actions(self, actions):
        @actions.add(".sip", 1)
        def _m_sip(agent, term, intention):
            print("[owner] sipping")
            # un 25% de prob de acabar la cerveza en este trago
            if random.random() < 0.25:
                self.bdi.remove_belief("has","owner","beer")
            yield


class MarketAgent(BDIAgent):
    def add_custom_actions(self, actions):
        @actions.add(".deliver", 2)
        def _m_deliver(agent, term, intention):
            args = agentspeak.grounded(term.args, intention.scope)
            prod = args[0]
            qty = args[1]
            print("[market] delivering order",str(qty),prod)
            print("[market] done")
            yield


async def main():
    robot = RobotAgent("robot@localhost", "1234", "robot.asl")
    owner = OwnerAgent("owner@localhost", "1234", "owner.asl")
    market = MarketAgent("market@localhost", "1234", "supermarket.asl")

    print("setting robot")
    # establece el stock inicial and owner
    robot.set_stock(1)
    robot.set_owner(owner)
    print("Start agents" )
    await market.start()
    await robot.start()
    await owner.start()
    await asyncio.sleep(10)


    print("Stop agents...")
    print("** final robot beliefs ")
    robot.bdi.print_beliefs()
    print("** final owner beliefs ")
    owner.bdi.print_beliefs()
    print("** final market beliefs ")
    market.bdi.print_beliefs()
    await robot.stop()
    await owner.stop()
    await market.stop()
    print("Agents stopped")


if __name__ == "__main__":
    spade.run(main())