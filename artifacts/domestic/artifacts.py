import asyncio
import random
from spade_artifact import Artifact

class Beer(Artifact):
    """Artefacto cerveza."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = "full"

    async def setup(self):
        await self.publish(self.state)

    def sip(self):
        """Acción de beber."""
        if self.state == "full":
            if random.random() < 0.25:
                self.state = "empty"
                print(f"[{self.jid}] Empty! (I finished my beer)")
                if hasattr(self, "pubsub") and self.pubsub:
                    asyncio.create_task(self.publish(self.state))
            else:
                print(f"[{self.jid}] Slurp... still some left.")


class Fridge(Artifact):
    """La nevera es un contenedor de objetos Beer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.beers = []

    def set_stock(self, instances):
        self.beers = instances

    async def setup(self):
        state = "available" if len(self.beers) > 0 else "empty"
        await self.publish(state)

    def _publish_availability(self):
        state = "available" if len(self.beers) > 0 else "empty"
        if hasattr(self, "pubsub") and self.pubsub:
            asyncio.create_task(self.publish(state))

    def open(self):
        if hasattr(self, "pubsub") and self.pubsub:
            asyncio.create_task(self.publish(f"stock:{len(self.beers)}"))

    def take(self):
        if self.beers:
            beer = self.beers.pop(0)
            if hasattr(self, "pubsub") and self.pubsub:
                asyncio.create_task(self.publish(f"stock:{len(self.beers)}"))
            return beer
        return None

    def restock(self, new_beers):
        self.beers.extend(new_beers)
        self._publish_availability()
