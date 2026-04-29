# Guia Practica y Tutorial Tecnico de Simulacion de Trafico

Este documento detalla la integracion tecnologica del laboratorio y describe la ejecucion de pruebas de bajo nivel, la arquitectura reactiva del sistema y el comportamiento de la red de carreteras.

---

## 1. Validacion de la Infraestructura mediante Tests

Si experimentas problemas de visualizacion o bloqueos de red, debes recurrir a los scripts puros de validacion en `tests/`. Estos archivos prescinden del servidor Streamlit y operan directamente sobre sockets crudos de TraCI.

### Ejecucion de Pruebas

Lanza los comandos desde el directorio `sumo/`:

* **`uv run tests/test_standalone.py`**: Inicia SUMO en modo texto y renderiza un frame estatico de los carriles y vehiculos mediante `matplotlib.pyplot.scatter`. Ideal para verificar el soporte GUI.
* **`uv run tests/test_engine.py scenarios/cross/cross.sumocfg`**: Carga el motor `SumoEngine` y avanza los pasos mediante `plt.pause`.

---

## 2. Funcionamiento Interno del Dashboard (Streamlit)

La interfaz en `dashboard.py` es stateless (sin estado persistente). Cada vez que el usuario interactua con un slider de control o un desplegable:
1. Streamlit reinicia por completo el script de Python.
2. Para que esto no destruya el servidor TraCI en ejecucion, guardamos el objeto en `st.session_state.engine`.

La capa visual se redibuja continuamente a peticion del usuario solicitando listas de identificadores e iterando sobre coordenadas flotantes de posicion global (X, Y).

---

## 3. Desglose Pedagogico de Escenarios

Los alumnos deben resolver los problemas de coordinacion en orden secuencial:

1. **street**: Una unica recta. Pensada para familiarizarse con las llamadas basicas y el calculo de aceleracion.
2. **cross**: Interseccion tipica. Requiere alternar luces verdes sin colisiones.
3. **diagonal**: Introduce angulos no rectos que alteran la percepcion visual.
4. **dayuan**: Flujos circulares continuos donde el rendimiento de paso es critico.
5. **grid**: Reticula 3x3. Un semaforo mal coordinado puede causar un atasco en cascada.
6. **graph**: Rutas reales de Valencia. Calles estrechas y topologias no uniformes.
7. **random**: Entornos unicos. Obligan a disenar heuristicas generales.
8. **autonomous**: Intersecciones cerradas con vehiculos que no respetan prioridades humanas.
9. **interurban**: Autopistas donde el cambio de carril es el factor clave.

---

## 4. Fundamentos Tecnicos: SUMO y TraCI

### El Modelo de Simulacion
SUMO es un simulador microscopico: cada vehiculo cuenta con atributos individuales (velocidad maxima, desaceleracion, longitud). En cada paso discreto de tiempo (`time_step` por defecto 1 segundo), se calcula:
* **Modelo de seguimiento (Car-Following)**: Krauss o IDM. Calcula la distancia de seguridad con el lider.
* **Cambio de carril**.

### El Protocolo TraCI
TraCI se basa en una arquitectura TCP orientada a comandos. Python actua como cliente y SUMO como servidor. 

Instrucciones criticas:
* `traci.simulationStep()`: Ordena avanzar el reloj del servidor.
* `traci.vehicle.getSpeed(veh_id)`: Obtiene velocidad en metros por segundo.
* `traci.trafficlight.setPhase(tls_id, index)`: Fuerza el estado del semaforo.
