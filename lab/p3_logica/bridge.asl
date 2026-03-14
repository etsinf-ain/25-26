/* DOMAIN: bridge and torch */

// Times Ángela (1), Boris (2), Carmen (5) and Damian (8) with total limit 15.
// State: state(A, B, C, D, TorchSide, Elapsed)
// A,B,C,D are left/right positions for each person.
// TorchSide is the position of the torch.
// Elapsed is the total time elapsed (needed to prune paths exceeding max_time).
initial_state(state(left, left, left, left, left, 0)).
max_time(15).
time(angela, 1).
time(boris, 2).
time(carmen, 5).
time(damian, 8).

goal_state(state(right, right, right, right, right, Elapsed)) :-
    max_time(Max) &
    Elapsed <= Max.

unsafe(state(_, _, _, _, _, Elapsed)) :-
    max_time(Max) &
    Elapsed > Max.

opposite(left, right).
opposite(right, left).

// Crossing cost: max of the two persons' times.
cross_cost(P1, P2, Cost) :-
    time(P1, T1) &
    time(P2, T2) &
    .max([T1, T2], Cost).


/* MOVES — move(State, NextState, Action)
   One or two persons cross with the torch.
   The action term embeds the crossing cost for readability.
*/

// One-person crossings
move(state(SA, B, C, D, SA, Elapsed), state(NSA, B, C, D, NSA, NewElapsed), cross(angela, Cost)) :-
    opposite(SA, NSA) &
    time(angela, Cost) &
    NewElapsed = Elapsed + Cost &
    not unsafe(state(NSA, B, C, D, NSA, NewElapsed)).

move(state(A, SB, C, D, SB, Elapsed), state(A, NSB, C, D, NSB, NewElapsed), cross(boris, Cost)) :-
    opposite(SB, NSB) &
    time(boris, Cost) &
    NewElapsed = Elapsed + Cost &
    not unsafe(state(A, NSB, C, D, NSB, NewElapsed)).

move(state(A, B, SC, D, SC, Elapsed), state(A, B, NSC, D, NSC, NewElapsed), cross(carmen, Cost)) :-
    opposite(SC, NSC) &
    time(carmen, Cost) &
    NewElapsed = Elapsed + Cost &
    not unsafe(state(A, B, NSC, D, NSC, NewElapsed)).

move(state(A, B, C, SD, SD, Elapsed), state(A, B, C, NSD, NSD, NewElapsed), cross(damian, Cost)) :-
    opposite(SD, NSD) &
    time(damian, Cost) &
    NewElapsed = Elapsed + Cost &
    not unsafe(state(A, B, C, NSD, NSD, NewElapsed)).

// Two-person crossings
move(state(SA, SB, C, D, SA, Elapsed), state(NSA, NSA, C, D, NSA, NewElapsed), cross(angela, boris, Cost)) :-
    SA == SB &
    opposite(SA, NSA) &
    cross_cost(angela, boris, Cost) &
    NewElapsed = Elapsed + Cost &
    not unsafe(state(NSA, NSA, C, D, NSA, NewElapsed)).

move(state(SA, B, SC, D, SA, Elapsed), state(NSA, B, NSA, D, NSA, NewElapsed), cross(angela, carmen, Cost)) :-
    SA == SC &
    opposite(SA, NSA) &
    cross_cost(angela, carmen, Cost) &
    NewElapsed = Elapsed + Cost &
    not unsafe(state(NSA, B, NSA, D, NSA, NewElapsed)).

move(state(SA, B, C, SD, SA, Elapsed), state(NSA, B, C, NSA, NSA, NewElapsed), cross(angela, damian, Cost)) :-
    SA == SD &
    opposite(SA, NSA) &
    cross_cost(angela, damian, Cost) &
    NewElapsed = Elapsed + Cost &
    not unsafe(state(NSA, B, C, NSA, NSA, NewElapsed)).

move(state(A, SB, SC, D, SB, Elapsed), state(A, NSB, NSB, D, NSB, NewElapsed), cross(boris, carmen, Cost)) :-
    SB == SC &
    opposite(SB, NSB) &
    cross_cost(boris, carmen, Cost) &
    NewElapsed = Elapsed + Cost &
    not unsafe(state(A, NSB, NSB, D, NSB, NewElapsed)).

move(state(A, SB, C, SD, SB, Elapsed), state(A, NSB, C, NSB, NSB, NewElapsed), cross(boris, damian, Cost)) :-
    SB == SD &
    opposite(SB, NSB) &
    cross_cost(boris, damian, Cost) &
    NewElapsed = Elapsed + Cost &
    not unsafe(state(A, NSB, C, NSB, NSB, NewElapsed)).

move(state(A, B, SC, SD, SC, Elapsed), state(A, B, NSC, NSC, NSC, NewElapsed), cross(carmen, damian, Cost)) :-
    SC == SD &
    opposite(SC, NSC) &
    cross_cost(carmen, damian, Cost) &
    NewElapsed = Elapsed + Cost &
    not unsafe(state(A, B, NSC, NSC, NSC, NewElapsed)).


/* --- SOLVER ---
   Elapsed is part of the state (needed for pruning via unsafe/1).
   Cycle detection uses only the structural part pos(A,B,C,D,Torch),
   extracted by pattern-matching the result of move directly.
*/
!start.


solve(Current, _, []) :- goal_state(Current).

solve(Current, Visited, Path) :-
    move(Current, state(A,B,C,D,T,E), Action) &
    not .member(pos(A,B,C,D,T), Visited) &
    .concat([pos(A,B,C,D,T)], Visited, NewVisited) &
    solve(state(A,B,C,D,T,E), NewVisited, Rest) &
    .concat([Action], Rest, Path).

+!start <-
    ?initial_state(S0);
    !start_solve(S0).

+!start_solve(S0) : solve(S0, [pos(left,left,left,left,left)], Path) <-
    .print("Initial state: ", S0);
    .print("Solution: ", Path).

+!start_solve(S0) : not solve(S0, [pos(left,left,left,left,left)], _) <-
    .print("Initial state: ", S0);
    .print("No solution found.").
