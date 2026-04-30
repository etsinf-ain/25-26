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

## Interpretación de Semáforos

Al consultar el estado de un semáforo con `traci.trafficlight.getRedYellowGreenState(id)`, recibirás una cadena de caracteres. Cada carácter representa un movimiento (link) controlado por esa intersección:

| Carácter | Significado | Descripción |
| :---: | :--- | :--- |
| **`G`** | Verde prioritario | Los vehículos avanzan sin restricciones. |
| **`g`** | Verde no prioritario | Permite el paso, pero cediendo el paso a flujos contrarios. |
| **`r`** / **`R`** | Rojo | Detención obligatoria. |
| **`y`** / **`Y`** | Amarillo | Fase de transición a rojo. |
| **`o`** | Apagado | El semáforo no está operativo. |

La longitud de la cadena depende de la complejidad del cruce. Por ejemplo, en una intersección de dos carreteras con dos carriles cada una, verás secuencias de 16 caracteres organizadas en cuatro grupos por cada entrada (Norte, Este, Sur, Oeste). Cada semáforo del cruce indica cuatro posibles movimientos: giro derecha, recto, giro izquierda y cambio de sentido.

### Ejemplo: Escenario 'Cross'
En el escenario de ejemplo `cross`, el semáforo `center` controla 16 movimientos. Si el agente imprime:
`Semáforo 'center': GGggrrrrGGggrrrr`

Esto se interpreta como:
*   **`GGgg`** (Norte): Flujo abierto.
*   **`rrrr`** (Este): Detenidos.
*   **`GGgg`** (Sur): Flujo abierto.
*   **`rrrr`** (Oeste): Detenidos.

En este estado, los vehículos pueden circular en el eje Norte-Sur, mientras que el tráfico del eje Este-Oeste permanece detenido en rojo.


