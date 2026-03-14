/* DOMAIN: 2x2 Sliding Tile Puzzle */
// Board indices:
// 0(A) 1(B)
// 2(C) 3(D)
// 0 is the empty tile.

// Initial State
initial_state(p(1, 2, 0, 3)).
// Goal: 1 2 / 3 0
goal_state(p(1, 2, 3, 0)).

// MOVES (Swapping Empty Tile 0 with Neighbors)

// Move Left (Gap moves Left, effectively Tile moves Right)
// (From B to A)
move(p(A, 0, C, D), p(0, A, C, D), "slide_left_row0") :- true.
// (From D to C)
move(p(A, B, C, 0), p(A, B, 0, C), "slide_left_row1") :- true.

// Move Right (Gap moves Right, Tile moves Left)
// (From A to B)
move(p(0, B, C, D), p(B, 0, C, D), "slide_right_row0") :- true.
// (From C to D)
move(p(A, B, 0, D), p(A, B, D, 0), "slide_right_row1") :- true.

// Move Up (Gap moves Up)
// (From C to A)
move(p(A, B, 0, D), p(0, B, A, D), "slide_up_col0") :- true.
// (From D to B)
move(p(A, B, C, 0), p(A, 0, C, B), "slide_up_col1") :- true.

// Move Down (Gap moves Down)
// (From A to C)
move(p(0, B, C, D), p(C, B, 0, D), "slide_down_col0") :- true.
// (From B to D)
move(p(A, 0, C, D), p(A, D, C, 0), "slide_down_col1") :- true.


/* --- SOLVER PATTERN --- */

solve(Current, _, []) :- goal_state(Current).
solve(Current, Visited, Path) :-
    move(Current, Next, Action) &
    not .member(Next, Visited) &
    .concat([Next], Visited, NewVisited) &
    solve(Next, NewVisited, Rest) &
    .concat([Action], Rest, Path).

!start.

+!start <-
    ?initial_state(S0);
    !start_solve(S0, [S0]).

+!start_solve(S0, V0) : solve(S0, V0, Path) <-
    .print("Puzzle Start: ", S0);
    .print("Solution: ", Path).

+!start_solve(S0, V0) : not solve(S0, V0, _) <-
    .print("Puzzle Start: ", S0);
    .print("No solution found.").
