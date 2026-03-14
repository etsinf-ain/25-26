/* DOMAIN: bridge and torch – generalized version */

// State: state(Positions, TorchSide, Elapsed)
// Positions is a list of pos(Person, Side).
// Elapsed is part of the state (needed for pruning via unsafe/1).
initial_state(state([pos(angela,left), pos(boris,left), pos(carmen,left), pos(damian,left)], left, 0)).
max_time(15).
time(angela, 1).
time(boris, 2).
time(carmen, 5).
time(damian, 8).

// Goal: all persons on the right and within time.
goal_state(state(Positions, right, Elapsed)) :-
    all_right(Positions) &
    not unsafe state(Positions, right, Elapsed).

// Unsafe if time exceeded.
unsafe(state(_, _, Elapsed)) :-
    max_time(Max) &
    Elapsed > Max.

// recursive rule for 'all people in right side' check
all_right([]) :- true.
all_right([pos(_, right) | Rest]) :- all_right(Rest).

opposite(left, right).
opposite(right, left).

// get_pos is needed (not replaceable by .member) because P is unbound when
// called — it does unification-based search to bind P to whoever is on
// side Torch. pyson's .member only checks membership of a ground element.
// set_pos is needed because there is no stdlib action for list update.
get_pos(P, [pos(P, Side) | _], Side) :- true.
get_pos(P, [_ | Rest], Side) :- get_pos(P, Rest, Side).

set_pos(P, Side, [pos(P, _) | Rest], [pos(P, Side) | Rest]) :- true.
set_pos(P, Side, [H | Rest], [H | NewRest]) :- set_pos(P, Side, Rest, NewRest).

// Crossing cost: max of the two persons' times.
cross_cost(P1, P2, Cost) :-
    P1 \== P2 &
    time(P1, T1) &
    time(P2, T2) &
    .max([T1, T2], Cost).


// MOVES — move(State, NextState, Action)
// The action term includes the crossing cost for readability.

// One person crosses with the torch.
move(state(Positions, Torch, Elapsed), state(NewPositions, NewTorch, NewElapsed), cross(P, Cost)) :-
    get_pos(P, Positions, Torch) &
    opposite(Torch, NewTorch) &
    time(P, Cost) &
    NewElapsed = Elapsed + Cost &
    set_pos(P, NewTorch, Positions, NewPositions) &
    not unsafe(state(NewPositions, NewTorch, NewElapsed)).

// Two persons cross together with the torch.
move(state(Positions, Torch, Elapsed), state(NewPositions, NewTorch, NewElapsed), cross(P1, P2, Cost)) :-
    get_pos(P1, Positions, Torch) &
    get_pos(P2, Positions, Torch) &
    opposite(Torch, NewTorch) &
    cross_cost(P1, P2, Cost) &
    NewElapsed = Elapsed + Cost &
    set_pos(P1, NewTorch, Positions, TmpPositions) &
    set_pos(P2, NewTorch, TmpPositions, NewPositions) &
    not unsafe(state(NewPositions, NewTorch, NewElapsed)).

/* --- SOLVER ---
   Elapsed is part of the state (needed for pruning via unsafe/1).
   Cycle detection uses only the structural part state(Positions, Torch),
   extracted by inline pattern-matching of move's second argument.
*/
!start.

solve(Current, _, []) :- goal_state(Current).
solve(Current, Visited, Path) :-
    move(Current, state(Pos, T, E), Action) &
    not .member(state(Pos, T), Visited) &
    .concat([state(Pos, T)], Visited, NewVisited) &
    solve(state(Pos, T, E), NewVisited, Rest) &
    .concat([Action], Rest, Path).

// instead using initial_state(S0) weneed to detail the initial state
+!start <-
    ?initial_state(state(Pos, T, E));
    !start_solve(state(Pos, T, E), [state(Pos, T)]).

+!start_solve(S0, V0) : solve(S0, V0, Path) <-
    .print("Initial state: ", S0);
    .print("Solution: ", Path).

+!start_solve(S0, V0) : not solve(S0, V0, _) <-
    .print("Initial state: ", S0);
    .print("No solution found.").
