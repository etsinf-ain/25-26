/* Objetivo inicial */
!print_fact(5).

/* Planes */
// logro: imprimir el factorial de 5
+!print_fact(N)
    <-
    // ¿qué ocurre si lo cambio por !!fact(N,F)?
    !fact(N,F);
    .print("fact(5) == ", F).

// unifica FF a 1 cuando N llega a 0
+!fact(N,1) : N == 0.

// recursión:
+!fact(N,F) : N > 0 <-
    !fact(N-1, FF);
    F = FF * N.