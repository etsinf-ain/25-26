import random
import agentspeak
import asyncio
from abc import ABC, abstractmethod
from spade_bdi.bdi import BDIAgent
from spade_artifact import ArtifactMixin
from artifacts import Fridge, Beer

# ── Base para agentes que usan la nevera ──────────────────────────────────────
class FridgeUserAgent(ArtifactMixin, BDIAgent, ABC):
    def __init__(self, *args, fridge_jid: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fridge_jid = fridge_jid
        self.fridge = None
        self._known_stock = None

    def fridge_callback(self, artifact_jid, state):
        if state == "available":
            self.bdi.set_belief("available", "beer", "fridge")
        elif state == "empty":
            self.bdi.remove_belief("available", "beer", "fridge")
        elif state.startswith("stock:"):
            self._known_stock = int(state.split(":")[1])
            self.bdi.set_belief("stock", "beer", self._known_stock)
            # Quitamos el print de aquí para evitar redundancia en consola
            if self._known_stock > 0: self.bdi.set_belief("available", "beer", "fridge")
            else: self.bdi.remove_belief("available", "beer", "fridge")

    def controls(self, fridge: Fridge):
        self.fridge = fridge

    async def setup(self):
        await self.artifacts.focus(self.fridge_jid, self.fridge_callback)

    def _add_fridge_actions(self, actions):
        @actions.add(".open", 1)
        def _m_open(agent, term, intention):
            print(f"[{self.name}] opening fridge")
            self.fridge.open()
            yield

        @actions.add(".close", 1)
        def _m_close(agent, term, intention):
            print(f"[{self.name}] closing fridge")
            if self._known_stock is not None:
                self.bdi.remove_belief("stock", "beer", self._known_stock)
                self._known_stock = None
            yield

    @abstractmethod
    def add_custom_actions(self, actions):
        pass


# ── Agente Camarero (Waiter) ──────────────────────────────────────────────────
class WaiterAgent(FridgeUserAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = None
        self.held_beer = None 

    def set_owner(self, owner):
        self.owner = owner

    def add_custom_actions(self, actions):
        self._add_fridge_actions(actions)

        @actions.add(".get", 1)
        def _m_get(agent, term, intention):
            self.held_beer = self.fridge.take()
            if self.held_beer:
                print(f"[{self.name}] taking {self.held_beer.jid}")
                self.bdi.set_belief("holding", "beer")
            yield

        @actions.add(".hand_in", 1)
        def _m_hand_in(agent, term, intention):
            if self.held_beer:
                print(f"[{self.name}] giving beer to owner")
                self.owner.receive_beer(self.held_beer)
                self.owner.bdi.set_belief("has", "owner", "beer")
                self.held_beer = None
                self.bdi.remove_belief("holding", "beer")
            yield

        @actions.add(".move_towards", 1)
        def _m_move_towards(agent, term, intention):
            args = agentspeak.grounded(term.args, intention.scope)
            print(f"[{self.name}] moving towards {args[0]}...")
            self.bdi.set_belief("at", "robot", args[0])
            yield


# ── Agente Reponedor (Stocker) ────────────────────────────────────────────────
class StockerAgent(FridgeUserAgent):
    _beer_serial = 1

    def add_custom_actions(self, actions):
        self._add_fridge_actions(actions)

        @actions.add(".restock", 1)
        def _m_restock(agent, term, intention):
            args = agentspeak.grounded(term.args, intention.scope)
            qty = int(args[0])
            asyncio.create_task(self._do_physical_restock(qty))
            yield

    async def _do_physical_restock(self, qty):
        new_beers = []
        for _ in range(qty):
            jid = f"beer_{StockerAgent._beer_serial}@localhost"
            print(f"[{self.name}] preparing {jid}...")
            b = Beer(jid, "1234")
            await b.start() 
            new_beers.append(b)
            StockerAgent._beer_serial += 1
        
        print(f"[{self.name}] all beers ready. Putting in fridge.")
        self.fridge.restock(new_beers)


# ── Agente Dueño (Owner) ──────────────────────────────────────────────────────
class OwnerAgent(ArtifactMixin, BDIAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_beer_obj = None
        self.current_beer_jid = None

    def beer_callback(self, artifact_jid, state):
        if state == "empty":
            jid_to_ignore = str(artifact_jid) if (artifact_jid and str(artifact_jid) != "") else self.current_beer_jid
            print(f"[{self.name}] Detected empty beer: {jid_to_ignore}. Stopping artifact.")
            self.bdi.remove_belief("has", "owner", "beer")
            self.bdi.remove_belief("focused", "beer")
            if self.current_beer_obj:
                asyncio.create_task(self.current_beer_obj.stop())
            self.current_beer_obj = None
            self.current_beer_jid = None

    def receive_beer(self, beer_obj):
        self.current_beer_obj = beer_obj
        self.current_beer_jid = str(beer_obj.jid)
        asyncio.create_task(self._secure_focus(self.current_beer_jid))

    async def _secure_focus(self, jid):
        await self.artifacts.focus(jid, self.beer_callback)
        print(f"[{self.name}] Focus established on {jid}. Ready to sip.")
        self.bdi.set_belief("focused", "beer")

    def add_custom_actions(self, actions):
        @actions.add(".sip", 1)
        def _m_sip(agent, term, intention):
            if self.current_beer_obj:
                self.current_beer_obj.sip()
            yield


# ── Agente Supermercado (Market) ──────────────────────────────────────────────
class MarketAgent(BDIAgent):
    def add_custom_actions(self, actions):
        @actions.add(".deliver", 2)
        def _m_deliver(agent, term, intention):
            args = agentspeak.grounded(term.args, intention.scope)
            print(f"[{self.name}] delivering {args[1]} {args[0]}...")
            yield
