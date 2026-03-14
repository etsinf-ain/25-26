/* DOMAIN: Towers of Hanoi (3 Disks) */

// Disks are integers 1 (smallest) to N (largest).
// State: state(Pole1, Pole2, Pole3) where each Pole is a list [Top, ..., Bottom]
initial_state(state([1,2,3], [], [])).
goal_state(state([], [], [1,2,3])).

// VALID MOVE LOGIC
// Can place Disk D on Pole P if P is empty OR Head(P) > D.
can_place(D, []) :- true.
can_place(D, [Top | _]) :- D < Top.

// MOVES

// 1. Move from Pole 1 to Pole 2
move(state([D|Rest1], P2, P3), state(Rest1, [D|P2], P3), move_1_to_2) :-
    can_place(D, P2).

// 2. Move from Pole 1 to Pole 3
move(state([D|Rest1], P2, P3), state(Rest1, P2, [D|P3]), move_1_to_3) :-
    can_place(D, P3).

// 3. Move from Pole 2 to Pole 1
move(state(P1, [D|Rest2], P3), state([D|P1], Rest2, P3), move_2_to_1) :-
    can_place(D, P1).

// 4. Move from Pole 2 to Pole 3
move(state(P1, [D|Rest2], P3), state(P1, Rest2, [D|P3]), move_2_to_3) :-
    can_place(D, P3).

// 5. Move from Pole 3 to Pole 1
move(state(P1, P2, [D|Rest3]), state([D|P1], P2, Rest3), move_3_to_1) :-
    can_place(D, P1).

// 6. Move from Pole 3 to Pole 2
move(state(P1, P2, [D|Rest3]), state(P1, [D|P2], Rest3), move_3_to_2) :-
    can_place(D, P2).


/* --- SOLVER PATTERN INCLUDED BELOW --- */
!start. 

solve(Current, _, []) :- goal_state(Current).
solve(Current, Visited, Path) :-
    move(Current, Next, Action) &
    not .member(Next, Visited) &
    .concat([Next], Visited, NewVisited) &
    solve(Next, NewVisited, Rest) &
    .concat([Action], Rest, Path).

+!start <-
    ?initial_state(S0);
    !start_solve(S0).

+!start_solve(S0) : solve(S0, [S0], Path) <-
    .print("Hanoi Start: ", S0);
    .print("Hanoi Solution: ", Path).

+!start_solve(S0) : not solve(S0, [S0], _) <-
    .print("Hanoi Start: ", S0);
    .print("No solution found.").