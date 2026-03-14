time(angela, 1).
time(boris, 2).
time(carmen, 5).
time(damian, 8).

cross_cost(P1, P2, Cost) :-
    time(P1, T1) &
    time(P2, T2) &
    P1 \== P2 &
    .min([T1, T2], Cost).

!start.

+!start <-
    ?cross_cost(P1,P2,Cost) ;
    .print(P1, P2, Cost).