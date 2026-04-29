/* Rules */

// Rule to check whenever all participants have answered
// counting the number of participants of each type
all_proposals_received :- 
  .count(propose(_), NP) &     // number of proposes received
  .count(refuse, NR) &         // number of refusals received
  NP + NR == 4.

/* Initial goals */
!start. 

/* Plans */

// start the CNP sending the cfp to all participants
+!start
   <- 
      .print("Sending call for proposals...");
      .send("part1@localhost",achieve,cfp);
      .send("part2@localhost",achieve,cfp);
      .send("part3@localhost",achieve,cfp);
      .send("reject@localhost",achieve,cfp);
      .print("Waiting for proposals...");
      +state(wfp).

// process the proposals received
+refuse([source(A)])
   <- .print("Refusal received from", A).

+propose(Offer)[source(A)]
   <- .print("Proposal received from", A, "with offer", Offer);
      +offer(Offer,A). // save the offer in a belief to be used later   

+offer(Offer,Agent) : all_proposals_received & state(wfp)
   <- 
      .print("All offers received, selecting the best...");
      -state(_);
      !select.

+offer(Offer,Agent) : not all_proposals_received
   <- 
   .count(offer(_,_), NO);      // number of proposes received
   .print(NO, "offers received. Still waiting").

// select the best proposal and announce the result
+!select
   <-
      // creates a list [L] 
      .findall(offer(O,A),propose(O)[source(A)],L);
      .print("Offers are ",L);
      L \== []; // at least one offer

      // sort offers, the first is the best
      .max(L,offer(WinOf,WinAg)); 
      .print("Winner is ",WinAg," with ",WinOf);
      // announce the result to all participants
      !announce_result(L,WinAg).


// announce the result of the CNP to all participants
//all announces sent (empty list -> recursion done)
+!announce_result([],_).

// announce to others
+!announce_result([offer(O,LoserAg)|T],WinAg) : LoserAg \== WinAg
   <- .send(LoserAg,tell,reject);
      !announce_result(T,WinAg).

// announce to the winner
+!announce_result([offer(O,Ag)|T],WinAg) : Ag == WinAg
   <- .send(WinAg,tell,accept);
      !announce_result(T,WinAg).

// task done. Process completed
+inform("done")[source(A)]
   <- .print("Task done, informed by", A).