# SUMO Multi-Agent Traffic Laboratory

Este proyecto proporciona un entorno interactivo y visual para experimentar con la simulación de tráfico y sistemas multiagente (MAS). Integra Eclipse SUMO (Simulation of Urban MObility) con interfaces de control en Python y un panel web dinámico desarrollado en Streamlit.

## Inicio Rapido

### Requisitos Previos

1. **Eclipse SUMO**: Es obligatorio tener instalado SUMO en el sistema operativo.
   * En macOS (usando Homebrew): `brew install sumo`
   * En Linux (Ubuntu/Debian): `sudo apt-get install sumo sumo-tools sumo-doc`
2. **Variables de Entorno**: Configura las rutas necesarias en tu perfil de shell:
   * `SUMO_HOME`: Apunta a la base de la suite SUMO.
     * macOS: `/opt/homebrew/opt/sumo/share/sumo`
     * Linux: `/usr/share/sumo`
   * `PROJ_LIB`: Necesaria para el escenario `graph` (conversión de mapas OSM).
     * macOS: `/opt/homebrew/share/proj`
     * Linux: `/usr/share/proj`
     * Windows: `C:\Program Files\SUMO\share\proj`


### Instalación de dependencias

El entorno de ejecución está aislado dentro de la carpeta `sumo/` con su propio gestor de paquetes. Accede a la carpeta y sincroniza dependencias:
```bash
cd sumo
uv sync
```

### Ejecutar el Dashboard Visual

Inicia la interfaz de control principal lanzando:
```bash
uv run streamlit run dashboard.py
```

---

## Arquitectura de Archivos y Organización

* **`dashboard.py`**: Interfaz de usuario basada en Streamlit. Maneja selectores de escenarios y sliders de velocidad.
* **`sim_engine.py`**: El núcleo de la abstracción. Envuelve las llamadas de TraCI en un objeto `SumoEngine`.
* **`scenarios/`**: Subdirectorios con topologías específicas (mallas `.net.xml`, archivos de rutas `.rou.xml` y configuraciones `.sumocfg`).
* **`tools/`**: Utilidades independientes para generar escenarios.
* **`tests/`**: Suite de validación para garantizar que los puertos TCP y sockets funcionan sin dependencias de Streamlit.

Para profundizar en la programación de controladores y las fases de los semáforos, consulta `TUTORIAL.md`.
