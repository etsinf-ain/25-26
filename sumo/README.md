# SUMO Multi-Agent Traffic Laboratory

Este proyecto proporciona un entorno interactivo y visual para experimentar con la simulación de tráfico y sistemas multiagente (MAS). Integra Eclipse SUMO (Simulation of Urban MObility) con interfaces de control en Python y un panel web dinámico desarrollado en Streamlit.

## Inicio Rapido

### Requisitos Previos

1. **Eclipse SUMO**: Es obligatorio tener instalado SUMO en el sistema operativo.
   * En macOS (usando Homebrew): `brew install sumo`
   * En Linux (Ubuntu/Debian): `sudo apt-get install sumo sumo-tools sumo-doc`
   * En Windows: Descarga e instala el msi desde la [web oficial de SUMO](https://sumo.dlr.de/docs/Downloads.php).
2. **Variables de Entorno**: Configura las rutas necesarias en tu perfil de shell:
   * `SUMO_HOME`: Apunta a la base de la suite SUMO (revisa tu instalación para poner la ruta correcta).
     * macOS: `/opt/homebrew/opt/sumo/share/sumo`
     * Linux: `/usr/share/sumo`
     * Windows: `C:\Program Files\Eclipse\Sumo`


### Instalación de dependencias

El entorno de ejecución está aislado dentro de la carpeta `sumo/` con su propio gestor de paquetes. Accede a la carpeta y sincroniza dependencias:
```bash
cd sumo
uv sync
```

### Ejecutar el Dashboard Visual

Inicia la interfaz de control principal lanzando:
```bash
$ uv run streamlit run dashboard.py
```
S
---

## Arquitectura de Archivos y Organización

* **`dashboard.py`**: Interfaz de usuario basada en Streamlit. Maneja selectores de escenarios y sliders de velocidad.
* **`sim_engine.py`**: El núcleo de la abstracción. Envuelve las llamadas de TraCI en un objeto `SumoEngine`.
* **`scenarios/`**: Subdirectorios con topologías específicas:
    * `street`: Una única calle recta para pruebas iniciales de velocidad.
    * `basic_cross`: Intersección ortogonal simple de un carril por sentido.
    * `cross`: Intersección compleja con múltiples carriles y giros permitidos.
    * `diagonal`: Cruce con calles en ángulo para validar el motor visual.
    * `dayuan`: Escenario circular para flujos continuos de tráfico.
    * `grid`: Cuadrícula regular 3x3 para coordinar múltiples semáforos.
    * `random`: Base para la generación de ciudades aleatorias con semáforos.
    * `autonomous`: Red sin semáforos optimizada para protocolos V2X.
    * `interurban`: Tramo de autopista para modelos de cambio de carril.
    * `sensors_cross`: Cruce equipado con sensores físicos E1 (espiras) y E2 (áreas).
    * `full_sensorized`: Cuadrícula completa monitorizada automáticamente con detectores.
    * `random_sensorized`: Genera una ciudad aleatoria con detectores solo en los semáforos.
    * `mixed`: Escenario para pruebas de coexistencia (coches inteligentes -magenta- vs humanos -azules-).
* **`tools/`**: Utilidades de generación procedimental:
    * `build_random_city.py`: Crea una red en cuadrícula con avenidas y calles secundarias.
    * `build_autonomous_city.py`: Genera una red de prioridad sin semáforos.
    * `build_interurban.py`: Genera un tramo recto de autopista de varios carriles.
    * `build_random_sensorized.py`: Generador de ciudades aleatorias con sensores automáticos.
    * `build_mixed.py`: Generador de escenarios de tráfico mixto (magenta vs azul).
* **`examples/`**: Agentes de ejemplo y plantillas de integración:
    * `basic_agent.py`: Bucle de control básico mediante TraCI (Python puro).
    * `bdi_integration.py`: Plantilla de integración con SPADE-BDI y AgentSpeak.
    * `e1_sensor_agent.py`: Monitorización de sensores puntuales (induction loops).
    * `e2_sensor_agent.py`: Monitorización de sensores de área (lane area detectors).
    * `discovery_agent.py`: Agente para el descubrimiento automático de elementos de sumo.
    * `fcd_agent.py`: Detección por proximidad sin sensores físicos. Usa la posición de los vehículos para simular la detección.
    * `v2v_greeting.py`: Demostración de descubrimiento y comunicación directa entre vehículos.
* **`tests/`**: Suite de validación para sockets y TraCI.

Para profundizar en la programación de controladores y las fases de los semáforos, consulta `TUTORIAL.md`.

Para detalles sobre la implementación de sistemas multiagente y uso de sensores, consulta `AGENTS.md`.
