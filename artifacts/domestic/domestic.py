import asyncio
import spade
import logging
from artifacts import Fridge, Beer
from agents import WaiterAgent, StockerAgent, OwnerAgent, MarketAgent

# Silenciamos los logs de SPADE para limpiar la consola
logging.getLogger("spade").setLevel(logging.CRITICAL)
logging.getLogger("spade_artifact").setLevel(logging.CRITICAL)
logging.getLogger("spade_pubsub").setLevel(logging.CRITICAL)
# También para loguru si estuviera presente
try:
    from loguru import logger
    logger.remove()
except ImportError:
    pass

async def main():
    # 1. Instanciar Nevera (Vacía)
    fridge = Fridge("fridge@localhost", "1234")
    fridge.set_stock([])

    # 2. Instanciar Agentes
    waiter = WaiterAgent("waiter@localhost", "1234", "waiter.asl", fridge_jid="fridge@localhost")
    stocker = StockerAgent("stocker@localhost", "1234", "stocker.asl", fridge_jid="fridge@localhost")
    owner = OwnerAgent("owner@localhost", "1234", "owner.asl")
    market = MarketAgent("market@localhost", "1234", "supermarket.asl")

    # 3. Cruzar referencias
    waiter.controls(fridge)
    waiter.set_owner(owner)
    stocker.controls(fridge)

    # 4. Arrancar Artefactos
    print(">>> Iniciando entorno físico...")
    await fridge.start()

    # 5. Arrancar Agentes
    print(">>> Iniciando agentes...")
    await market.start()
    await waiter.start()
    await stocker.start()
    await owner.start()

    # 6. Ejecución infinita
    print("--- SISTEMA EN MARCHA (Presiona Ctrl+C para detener) ---")
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        # 7. Parada y Limpieza
        print("\n--- DETENIENDO SISTEMA ---")
        # Paramos agentes primero
        await waiter.stop()
        await stocker.stop()
        await owner.stop()
        await market.stop()
        # Paramos el entorno
        await fridge.stop()

        # 8. Mostrar creencias finales
        print("" + "="*40)
        print(" ESTADO FINAL DE LAS CREENCIAS BDI")
        print("="*40)
        print("** [OWNER]")
        owner.bdi.print_beliefs()
        print("** [WAITER]")
        waiter.bdi.print_beliefs()
        print("** [STOCKER]")
        stocker.bdi.print_beliefs()
        print("** [MARKET]")
        market.bdi.print_beliefs()
        print("="*40)
        print("Cierre finalizado.")

if __name__ == "__main__":
    spade.run(main())
