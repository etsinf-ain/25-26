/* agent that refuses the cfp */

// reject the cfp
+!cfp[source(A)] 
   <- 
   .print("CFP received from", A);
   .send(A,tell,refuse).

