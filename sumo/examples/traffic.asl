// Creencias iniciales
light_state(red).

// Regla: Si hay coches esperando en el Norte y el semáforo está rojo, cambiar a verde
+cars_waiting(lane, count) : count > 0 & light_state(red) <- 
    print("Detectados ", count, " coches en ", lane, ". Cambiando semáforo...");
    switch_phase;
    -+light_state(green).

// Regla: Si no hay coches, volver a rojo tras un tiempo (simplificado)
+cars_waiting(lane, 0) : light_state(green) <-
    print("Carril libre. Volviendo a rojo...");
    switch_phase;
    -+light_state(red).
