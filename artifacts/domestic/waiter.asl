/* waiter.asl */

limit(beer, 7).
too_much(beer) :-
    .date(YY,MM,DD) & 
    .count(consumed(YY,MM,DD,_,_,_,beer), QtdB) & 
    limit(beer, Limit) & 
    QtdB >= Limit.

at(robot, fridge).

+!has(Ow, B) : available(beer, fridge) & not too_much(beer)
    <- .print("I am getting a ", B, " for ", Ow);
       !at(robot, fridge);
       +serving(Ow, B);
       .open(fridge).

// Caso A: Hay stock, continuamos con las acciones originales
+stock(beer, Q) : serving(Ow, B) & Q > 0
    <- .print("Looking inside... there are ", Q, " beers.");
       .get(B);
       .close(fridge);
       -serving(Ow, B);
       !at(robot, owner);
       .hand_in(Ow);
       // register that another beer will be consumed
       .date(YY,MM,DD); .time(HH,NN,SS);
       +consumed(YY,MM,DD,HH,NN,SS,beer);
       .print("Enjoy your beer, ", Ow).

// Caso B: No hay stock (se queda esperando a que se reponga)
+stock(beer, 0) : serving(Ow, B)
    <- .print("Looking inside... there are 0 beers.");
       .close(fridge).

+!has(Ow, B) : not available(beer, fridge) & not too_much(beer)
    <- .print("Stock is empty. I will serve you as soon as it arrives.");
       +pedido_pendiente(Ow, B).

+available(beer, fridge) : pedido_pendiente(Ow, B)
    <- .print("Stock is back! Serving pending order for ", Ow);
       -pedido_pendiente(Ow, B);
       !has(Ow, B).

+!has(Ow, B) : too_much(beer)
    <- ?limit(beer, L);
       .concat("The Department of Health does not allow me to give you more than ", L, " beers a day!", M);
       .print(M);
       .send("owner@localhost", tell, msg(M));
       .print("Refusing to serve more beer to ", Ow).

+!at(robot, P) : at(robot, P) <- true.

+!at(robot, P) : not at(robot, P) 
    <- .print("Going to ", P);
       .move_towards(P);
       !at(robot, P).
