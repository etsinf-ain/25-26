/* Creencias */
// inicialmente la puerta está cerrada
locked.

/* Planes */
+locked <-
    .print("pide abrir");
    .send("porter@localhost",achieve,unlock);
    -locked.
