/* agent that participates normally in a cfp */

/* Plans */

// answer to Call For Proposal   
+!cfp[source(A)]
   <- 
      .print("CFP received from", A);
      .random(Offer); // get the price for the task
      .print("I propose ",Offer);
      +proposal(Offer); // remember my proposal
      .send(A,tell,propose(Offer)).
      
// proposal accepted -> do the task
+accept[source(A)]
   :  proposal(Offer)
   <- .print("My proposal ",Offer," won");
   -proposal(_); // remove the proposal's belief
      // do the task 
      .send(A,tell,inform("done")).
	       

// proposal refused -> do nothing and remove proposal
+reject
   <- .print("I lost CNP");
      -proposal(_). // remove the proposal's belief
	  

