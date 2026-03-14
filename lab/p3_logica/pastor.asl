/* DOMAIN: wolf, sheep and cabbage */

// State: state(wolf, sheep, cabbage, boat), 
// where each values can be left/right indicating the river bank.
initial_state(state(left, left, left, left)).
goal_state(state(right, right, right, right)).

    
// CONSTRAINTS
// 1. Wolf and sheep cannot be left alone on the same bank.
unsafe(state(Bank, Bank, _, Boat)) :- Bank \== Boat.
// 2. Sheep and cabbage cannot be left alone on the same bank.
unsafe(state(_, Bank, Bank, Boat)) :- Bank \== Boat.

opposite(left, right).
opposite(right, left).

// MOVES
// 1. Move wolf
move(state(B, S, C, B), state(NewB, S, C, NewB), move_wolf) :-
    opposite(B, NewB) &
    not unsafe(state(NewB, S, C, NewB)).

// 2. Move sheep
move(state(W, B, C, B), state(W, NewB, C, NewB), move_sheep) :-
    opposite(B, NewB) &
    not unsafe(state(W, NewB, C, NewB)).

// 3. Move cabbage
move(state(W, S, B, B), state(W, S, NewB, NewB), move_cabbage) :-
    opposite(B, NewB) &
    not unsafe(state(W, S, NewB, NewB)).

// 4. Move alone
move(state(W, S, C, B), state(W, S, C, NewB), move_alone) :-
    opposite(B, NewB) &
    not unsafe(state(W, S, C, NewB)).  
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