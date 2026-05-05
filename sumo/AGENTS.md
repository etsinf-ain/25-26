# Desarrollo de Sistemas Multiagente (MAS)

Este documento explica la implementacion de clientes autonomos conectados a la infraestructura de Eclipse SUMO.

## Mecanismo Multi-Cliente en TraCI

Por defecto, SUMO solo acepta un cliente TCP. Para permitir que coexistan el visualizador de Streamlit y el agente inteligente, se utiliza el sistema de prioridades de TraCI.

1. El visualizador actua como **Cliente 1**.
  
2. El agente actua como **Cliente 2**.
  

Ambos deben invocar secuencialmente `traci.simulationStep()`. SUMO sincronizara el paso de tiempo unicamente cuando haya recibido confirmacion de todos los clientes registrados.

## Programacion del Controlador

### Uso de Artefactos y Agentes Básicos

Para separar la logica de control del simulador, podemos usar **Artefactos**. Un artefacto actua como una abstraccion de un elemento fisico (como un semaforo o un sensor) que el agente puede observar y manipular.

Ejemplo: `basic_agent.py` muestra como crear un agente SPADE que se conecta a TraCI y utiliza un bucle de control simple para gestionar el trafico.

## Interpretación de Semáforos

Al consultar el estado de un semáforo con `traci.trafficlight.getRedYellowGreenState(id)`, recibirás una cadena de caracteres. Cada carácter representa un movimiento (link) controlado por esa intersección.

| Carácter | Significado | Descripción |

| :---: | :--- | :--- |

| **`G`** | Verde prioritario | Los vehículos avanzan sin restricciones. |

| **`g`** | Verde no prioritario | Permite el paso, pero cediendo el paso a flujos contrarios. |

| **`r`** / **`R`** | Rojo | Detención obligatoria. |

| **`y`** / **`Y`** | Amarillo | Fase de transición a rojo. |

###

### Ejemplo: Escenario 'Cross'

En el escenario `cross`, el semáforo `center` controla 16 movimientos. Una secuencia como `GGggrrrrGGggrrrr` indica que el eje Norte-Sur tiene el paso abierto mientras que el Este-Oeste esta detenido.

## Agentes BDI

Cuando la toma de decisiones requiere evaluar condiciones complejas (creencias) y perseguir objetivos (deseos), utilizamos la arquitectura **BDI (Belief-Desire-Intention)**.

- **Agentes SPADE-BDI**: Permiten programar la logica en **AgentSpeak** (archivos `.asl`).
  
- **Reglas y Planes**: El agente reacciona a cambios en el trafico segun sus reglas predefinidas.
  

Ejemplo: `bdi_integration.py` integra el motor BDI con SUMO, usando el archivo `traffic.asl` para definir la estrategia de control.

## Sensores e Identificación Automática

### Sensores Físicos (E1 y E2)

- **Induction Loops (E1)**: Detectan el paso puntual de un vehículo. Útiles para conteo.
  
- **Lane Area Detectors (E2)**: Monitorizan un área (ej: 50m). Permiten medir colas.
  

Ejemplos: `e1_sensor_agent.py` y `e2_sensor_agent.py`.

### Descubrimiento Automático de Elementos

En modelos complejos o aleatorios, el agente no conoce de antemano los IDs de los semáforos o sensores. Para ello se utiliza la técnica de **Discovery**. El agente interroga a TraCI al inicio para identificar todos los elementos disponibles y construir su propio mapa mental del escenario.

Ejemplo: `discovery_agent.py` automatiza la identificacion de la infraestructura de SUMO.

## Conducción Autónoma y V2X

### Detección Lógica (FCD)

En escenarios sin sensores fisicos, los agentes usan **FCD (Floating Car Data)**. El agente simula una "antena" que detecta coches por proximidad GPS.

Ejemplo: `fcd_agent.py`.

### Comunicación Vehículo-a-Vehículo (V2V)

Los coches inteligentes pueden descubrirse y comunicarse directamente para negociar el paso.

Ejemplo: `v2v_greeting.py`.