// Ya no necesitamos la creencia inicial estática, la recibiremos del artefacto

// Regla: Si hay coches esperando en un carril y el semáforo está rojo
+cars_waiting(Lane, Count) : Count > 7 & light_state(Lane, red) <- 
    .print("AGENTE: Detectados ", Count, " coches en ", Lane, ". El semáforo está rojo. Cambiando...");
    .switch_phase;
    // El artefacto publicará el nuevo estado, pero podemos actualizarlo aquí para ir más rápido
    -light_state(Lane, _).
    //+light_state(center, green).

// Regla: Si el carril se queda vacío y está en verde, volver a rojo
+cars_waiting(Lane, Count) : Count < 4 & light_state(Lane, green) <-
    .print("AGENTE: El carril ", Lane, " tiene menos de 4 coches. Volviendo a rojo");
    .switch_phase;
    -light_state(Lane, _).
    //+light_state(center, red).
