/* DOMAIN: missionaries and cannibals */

// State: state(MLeft, CLeft, Boat), 
// where each values can be left/right indicating the river bank.
initial_state(state(3, 3, left)).
goal_state(state(0, 0, right)).

// CONSTRAINTS
// 1. Cannibals cannot outnumber missionaries on the left
unsafe(state(MLeft, CLeft, _)) :- MLeft > 0 & CLeft > MLeft.

// 2. Cannibals cannot outnumber missionaries on the right
unsafe(state(MLeft, CLeft, _)) :-
    MRight = 3 - MLeft &
    CRight = 3 - CLeft &
    MRight > 0 &
    CRight > MRight.

// 3. Bounds for generated states.
//unsafe(state(MLeft, CLeft, _)) :- MLeft < 0.
//unsafe(state(MLeft, CLeft, _)) :- CLeft < 0.
//unsafe(state(MLeft, CLeft, _)) :- MLeft > 3.
//unsafe(state(MLeft, CLeft, _)) :- CLeft > 3.

// Valid boat loads: one or two persons.
trip(2, 0).
trip(0, 2).
trip(1, 1).
trip(1, 0).
trip(0, 1).

// MOVES
// Move from left to right.
move(state(MLeft, CLeft, left), state(NewMLeft, NewCLeft, right), move_right(M, C)) :-
    // valid trip
    trip(M, C) &
    // no more persons in the boat than on the left bank
    MLeft >= M &
    CLeft >= C &
    // calculate new state (substract persons in the boat)
    NewMLeft = MLeft - M &
    NewCLeft = CLeft - C &
    not unsafe(state(NewMLeft, NewCLeft, right)).

// Move from right to left.
move(state(MLeft, CLeft, right), state(NewMLeft, NewCLeft, left), move_left(M, C)) :-
    trip(M, C) &
    // calculate right bank counts
    MRight = 3 - MLeft &
    CRight = 3 - CLeft &
    // no more persons in the boat than on the right bank
    MRight >= M &
    CRight >= C &
    // calculate new state (add persons in the boat)
    NewMLeft = MLeft + M &
    NewCLeft = CLeft + C &
    not unsafe(state(NewMLeft, NewCLeft, left)).


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
    .print("Initial state: ", S0);
    .print("Solution: ", Path).

+!start_solve(S0) : not solve(S0, [S0], _) <-
    .print("Initial state: ", S0);
    .print("No solution found.").