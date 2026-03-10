/* Creencias */
// inicialmente la puerta está cerrada
locked.

/* Planes */

// recibe petición lock 
+!lock : unlocked 
    <-
    .print("cerrando heridas");
    +locked;
    -unlocked;
    .send("claustrophobic@localhost",tell,locked);
    .send("paranoid@localhost",tell,locked).

// recibe petición unlock
+!unlock : locked
    <-
    .print("abriendo puerta");
    +unlocked;
    -locked;
    .send("claustrophobic@localhost",tell,unlocked);
    .send("paranoid@localhost",tell,unlocked).
