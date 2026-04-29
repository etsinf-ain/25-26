/* owner.asl */

/* initial intention */
!get(beer).

// Pedir una cerveza
+!get(beer)
    <- .print("Asking for a beer");
       .send("waiter@localhost", achieve, has(owner, beer)).


// Si tengo una cerveza la bebo
+has(owner, beer)
    <- 
    !drink(beer).


// Si no tengo la cerveza la pido
-has(owner,beer) : true
    <- 
    .print("I drank the beer, I have no more beers! :(");
    .wait(1000);
    !get(beer).

// Proceso para beber cerveza dando tragos
+!drink(beer) : has(owner,beer)
    <- .sip(beer);
       !drink(beer).


// Fin de la recursion: no queda cerveza
+!drink(beer) : not has(owner,beer).


// Esperar si tengo la cerveza pero el foco aún no está listo
+!has(owner, beer) : has(owner, beer) & not focused(beer)
    <- .wait(100);
       !has(owner, beer).

// Reaccionar a mensajes del camarero
+msg(M)[source(Ag)] 
    <- .print("Message from ", Ag, ": ", M);
       -msg(M).