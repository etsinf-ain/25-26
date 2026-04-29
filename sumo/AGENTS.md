# Desarrollo de Sistemas Multiagente (MAS)

Este documento explica la implementacion de clientes autonomos conectados a la infraestructura de Eclipse SUMO.

## Mecanismo Multi-Cliente en TraCI

Por defecto, SUMO solo acepta un cliente TCP. Para permitir que coexistan el visualizador de Streamlit y el agente inteligente de toma de decisiones, se utiliza el sistema de prioridades de TraCI.

1. El visualizador actua como **Cliente 1**.
2. El agente actua como **Cliente 2**.

Ambos deben invocar secuencialmente `traci.simulationStep()`. SUMO sincronizara el paso de tiempo unicamente cuando haya recibido confirmacion de todos los clientes registrados.

## Programacion del Controlador

Accede a la carpeta `examples/` y utiliza `dummy_agent.py`.
```python
import traci

# El puerto se obtiene del panel de Streamlit
traci.init(port=8813)
traci.setOrder(2) # Prioridad 2 para el agente de control
```
A partir de este punto, puedes implementar algoritmos de optimizacion (como Q-Learning, Heuristicas por colas de espera o Redes Neuronales) capturando datos de entrada e inyectando ordenes sobre los semaforos.
