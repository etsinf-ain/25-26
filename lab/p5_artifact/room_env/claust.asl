/* Creencias */
// el estado inicial lo decine la clase Door


/* Planes */
+locked <-
    .print("pide abrir");
    .send("porter@localhost",achieve,unlock).