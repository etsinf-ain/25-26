// Creencias iniciales: torres [b,d,e], [g,f], [c,a]
on(e, table).
on(d, e).
on(b, d).
on(f, table).
on(g, f).
on(a, table).
on(c, a).

clear(X) :- not(on(_,X)).
tower([X]) :- on(X,table).
tower([X|Y|T]) :- on(X,Y) & tower([Y|T]).


// Estado final que se quiere alcanzar
!state([[f,d,c],[a,e,b],[g]]).


// Construye torres una a una
+!state([])    <- 
  .print("Finished!").

+!state([H|T]) <- 
  .print("build a tower", H);
  !tower(H); 
  !state(T).

// Torre construida -> fin
+!tower(T) : tower(T). 

// Torre de un solo bloque
+!tower([T])  <- 
  !on(T,table). 

// Descomposición en torres más pequeñas
+!tower([X|Y|T]) <- 
  !tower([Y|T]); 
  !on(X,Y). 

// conseguido
+!on(X,Y) : on(X,Y). 

// plan: conseguir bloques X, Y libres y apilar
+!on(X,Y) <- 
  !clear(X); 
  !clear(Y); 
  .move(X,Y);
  -on(X,_);
  +on(X,Y).

// la mesa siempre está libre
+!clear(table).

// conseguido
+!clear(X) : clear(X). 

// quitamos el bloque que hay encima de X y lo llevamos a la mesa
+!clear(X) :  
  on(H,X)
  <-
  !clear(H);
  .move(H,table);
  -on(H,_);
  +on(H,table).