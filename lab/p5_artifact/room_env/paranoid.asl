/* Creencias */
// el estado inicial lo decine la clase Door

/* Planes */
+unlocked <-
    .print("pide cerrar");
    .send("porter@localhost",achieve,lock).