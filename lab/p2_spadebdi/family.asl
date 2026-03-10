padre(X,Y) :- parent(X,Y) & hombre(X).


!start.

+!start <-
    +mujer(ana);
    +mujer(maria);
    +hombre(juan);
    +parent(ana,maria);
    +parent(juan,maria).

+parent(X,Y) : padre(X,Y)
<- +padre(X,Y).

+padre(X,Y) <-
    .print(X,"es el padre de",Y,"(plan)").

+parent(X,Y) : padre(X,Y) <-
    .print(X,"es padre de",Y,"(rule)").

+parent(X,Y) : hombre(X) 
    <-
    .print(X,"es padre de",Y,"(fact)").

+parent(X,Y) : mujer(X)
    <-
    .print(X,"es madre de",Y,"(fact)").