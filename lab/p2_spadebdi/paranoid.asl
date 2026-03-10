/* Creencias */
// inicialmente la puerta está cerrada
locked.

/* Planes */
+unlocked <-
    .print("pide cerrar");
    .send("porter@localhost",achieve,lock);
    -unlocked.