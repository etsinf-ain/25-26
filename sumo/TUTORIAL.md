# Guia Practica y Tutorial Tecnico de Simulacion de Trafico

Este documento detalla la integracion tecnologica del laboratorio y describe la ejecucion de pruebas de bajo nivel, la arquitectura reactiva del sistema y el comportamiento de la red de carreteras.

---

## 1. Validacion de la Infraestructura mediante Tests

Si experimentas problemas de visualizacion o bloqueos de red, debes recurrir a los scripts puros de validacion en `tests/`. Estos archivos prescinden del servidor Streamlit y operan directamente sobre sockets de TraCI.

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

Para lanzar el simulador, ejecuta el comando: 
`$ uv run streamlit run dashboard.py`
Abrirá un navegador web en `http://localhost:8501` con la interfaz del simulador.
Selecciona el escenario que quieras ejecutar en el desplegable de la barra lateral y pulsa [Start] para iniciar la simulacion.
Puedes ajustar la velocidad de la simulación usando el slider. Pulsa [Stop] cuando quieras detenerla. Puedes volver a pulsar [Start] para continuar la simulación o seleccionar una nueva.

Cuanto ejecutes una simulación, se muestra la semilla actual Seed. Puedes copiarla y pegarla luego en el parámetro `seed` de la simulación (debajo de la lista de escenarios) para poder reproducir la misma situación de tráfico.


---

## 3. Desglose de Escenarios

Esta es la secuenia de escenarios por orden de complejidad.

1. **street**: Una única recta. Pensada para familiarizarse con las llamadas básicas y el cálculo de aceleración.
2. **basic_cross**: Intersección ortogonal simple (sentido único). Ideal para el primer agente de semáforos.
3. **diagonal**: Introduce ángulos no rectos.
4. **dayuan**: Flujos circulares continuos donde el rendimiento de paso es crítico.
5. **cross**: Intersección más compleja (múltiples carriles y giros). Requiere alternar luces verdes sin colisiones
6. **grid**: Retícula 3x3 con calles de dos direcciones y semáforos
7. **random**: Grid 5x5 que combina avenidas de variso carriles con semáforos y calles de una dirección con prioridades de paso.
8. **autonomous**: Modelo equivalente al random sin semáforos, de manera que los vehículos se tienen que coordinar de manera autónoma.
9. **interurban**: Conexiones interurbanas con estructuras irregulares. Permite adelantamientos.
10. **sensors_cross**: Primera toma de contacto con sensores físicos (E1/E2) para monitorizar la situación del tráfico en los carriles.
11. **full_sensorized**: Modelo completamente sensorizado.
12. **mixed**: Escenario avanzado de coexistencia entre coches inteligentes y tráfico humano.

---

## 4. Fundamentos Tecnicos: SUMO y TraCI

### El Modelo de Simulacion
SUMO es un simulador de tráfico: cada vehiculo cuenta con atributos individuales (velocidad maxima, desaceleracion, longitud). En cada paso discreto de tiempo (`time_step` por defecto 1 segundo), se calcula:
* **Modelo de seguimiento (Car-Following)**: Krauss o IDM. Calcula la distancia de seguridad con el lider.
* **Cambio de carril**.
* **Prioridades de paso**.

### El Protocolo TraCI
TraCI es una biblioteca en python para el control del simulador SUMO. Se basa en una arquitectura TCP orientada a comandos. Python actua como cliente y SUMO como servidor. 

Instrucciones criticas:
w* `traci.simulationStep()`: Ordena avanzar el reloj del servidor.
* `traci.vehicle.getSpeed(veh_id)`: Obtiene velocidad en metros por segundo.
* `traci.trafficlight.setPhase(tls_id, index)`: Fuerza el estado del semaforo.

---

## 5. Referencia de Funciones TraCI (API de Python)

A continuación se detallan las funciones más utilizadas en los ejemplos, organizadas por el tipo de objeto que controlan:

### Control de la Simulación
* `traci.init(port)`: Conecta el script de Python con la instancia de SUMO que ya está en marcha.
* `traci.simulationStep()`: Avanza la simulación un paso de tiempo (normalmente 1 segundo).
* `traci.close()`: Finaliza la conexión de forma segura.
* `traci.junction.getIDList()`: Devuelve una lista con todos los nombres (IDs) de los cruces del mapa.
* `traci.junction.getPosition(id)`: Devuelve las coordenadas (X, Y) de un cruce específico.

### Semáforos (Traffic Lights)
* `traci.trafficlight.getIDList()`: Lista todos los semáforos del escenario.
* `traci.trafficlight.getRedYellowGreenState(id)`: Devuelve la cadena de caracteres (ej: "GGggrrrr") con el estado de las luces.
* `traci.trafficlight.setPhase(id, index)`: Cambia el semáforo a la fase indicada en el archivo de definición.
* `traci.trafficlight.setRedYellowGreenState(id, "state")`: Fuerza un estado manual para cada luz del semáforo.

### Vehículos
* `traci.vehicle.getIDList()`: Lista todos los vehículos que circulan actualmente por el mapa.
* `traci.vehicle.getSpeed(id)`: Devuelve la velocidad actual en m/s.
* `traci.vehicle.getPosition(id)`: Obtiene las coordenadas GPS (X, Y) actuales del coche.
* `traci.vehicle.getTypeID(id)`: Devuelve el tipo de vehículo (ej: "intelligent" o "normal").
* `traci.vehicle.getColor(id)`: Devuelve el color del vehículo en formato RGBA.

### Sensores y Detectores
* `traci.inductionloop.getIDList()`: Lista todos los sensores E1 (espiras) disponibles.
* `traci.inductionloop.getLastStepVehicleNumber(id)`: Conteo de vehículos que han cruzado el sensor en el último paso.
* `traci.lanearea.getIDList()`: Lista todos los sensores E2 (áreas) disponibles.
* `traci.lanearea.getJamLengthVehicle(id)`: Devuelve el número de vehículos parados (en cola) dentro del área del sensor.
* `traci.lanearea.getLastStepMeanSpeed(id)`: Velocidad media de todos los coches que están dentro del área.

---

## 6. Documentación Oficial y Recursos

Para consultas más profundas y detalles avanzados, puedes visitar las webs oficiales del proyecto:

* **Eclipse SUMO - Documentación Principal**: https://sumo.dlr.de/docs/
* **TraCI - Referencia Completa de la API**: https://sumo.dlr.de/docs/TraCI.html
* **Tutoriales de SUMO**: https://sumo.dlr.de/docs/Tutorials/index.html
