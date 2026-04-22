/* Creencias */
// el estado inicial lo decine la clase Door

/* Planes */

// recibe petición lock 
+!lock : unlocked //por seguridad (no es necesario)
    <-
    .print("cerrando heridas");
    .lock.

// recibe petición unlock
+!unlock : locked //por seguridad (no es necesario)
    <-
    .print("abriendo puerta");
    .unlock.

