/* DOMAIN: 8-puzzle (3x3 sliding tile puzzle) */
// Board: flat list of 9 elements, indices 0..8
//  0 1 2
//  3 4 5
//  6 7 8
// 0 represents the empty tile.

initial_state([1, 2, 3, 4, 5, 6, 0, 7, 8]).
goal_state([1, 2, 3, 4, 5, 6, 7, 8, 0]).

// Edge constraints: positions where each direction is blocked
left_edge(0).   left_edge(3).   left_edge(6).
right_edge(2).  right_edge(5).  right_edge(8).
top_edge(0).    top_edge(1).    top_edge(2).
bottom_edge(6). bottom_edge(7). bottom_edge(8).

// can_move(GapIdx, Direction, TileIdx)
// GapIdx: current index of the empty tile
// TileIdx: index of the tile that slides into the gap
can_move(GapIdx, left,  TileIdx) :- not left_edge(GapIdx)   & TileIdx = GapIdx - 1.
can_move(GapIdx, right, TileIdx) :- not right_edge(GapIdx)  & TileIdx = GapIdx + 1.
can_move(GapIdx, up,    TileIdx) :- not top_edge(GapIdx)    & TileIdx = GapIdx - 3.
can_move(GapIdx, down,  TileIdx) :- not bottom_edge(GapIdx) & TileIdx = GapIdx + 3.

// replace(List, Idx, NewVal, Result)
replace([_|T], 0, Val, [Val|T]) :- true.
replace([H|T], Idx, Val, [H|R]) :-
    Idx > 0 &
    Idx1 = Idx - 1 &
    replace(T, Idx1, Val, R).

// find_idx(List, Val, Idx): returns the index of Val in List
find_idx([Val|_], Val, 0) :- true.
find_idx([H|T], Val, Idx) :-
    H \== Val &
    find_idx(T, Val, Idx1) &
    Idx = Idx1 + 1.

// move(Board, NewBoard, Action): single rule for all 4 directions
move(Board, NewBoard, move(Dir)) :-
    find_idx(Board, 0, GapIdx) &
    can_move(GapIdx, Dir, TileIdx) &
    .nth(TileIdx, Board, Tile) &
    replace(Board, GapIdx, Tile, Tmp) &
    replace(Tmp, TileIdx, 0, NewBoard).

/* --- SOLVER --- */
solve(Current, _, []) :- goal_state(Current).
solve(Current, Visited, Path) :-
    move(Current, Next, Action) &
    not .member(Next, Visited) &
    .concat([Next], Visited, NewVisited) &
    solve(Next, NewVisited, Rest) & 
    .concat([Action], Rest, Path).

!start.

+!print_board(Board) <-
    .nth(0, Board, A); .nth(1, Board, B); .nth(2, Board, C);
    .nth(3, Board, D); .nth(4, Board, E); .nth(5, Board, F);
    .nth(6, Board, G); .nth(7, Board, H); .nth(8, Board, I);
    .print(A, B, C);
    .print(D, E, F);
    .print(G, H, I).

+!print_solution(_, []).
+!print_solution(Board, [Action|Rest]) <-
    move(Board, Next, Action);
    .print("--- ", Action, " ---");
    !print_board(Next);
    !print_solution(Next, Rest).

+!start <-
    ?initial_state(S0);
    !start_solve(S0, [S0]).

+!start_solve(S0, V0) : solve(S0, V0, Path) <-
    .print("Puzzle Start:");
    !print_board(S0);
    !print_solution(S0, Path).

+!start_solve(S0, V0) : not solve(S0, V0, _) <-
    .print("Puzzle Start:");
    !print_board(S0);
    .print("No solution found.").
