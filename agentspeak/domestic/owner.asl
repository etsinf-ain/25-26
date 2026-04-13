// Initial intention
!get(beer).
    
/* Set of plans */

// get a beer
+!get(beer) : true
    <- 
    .print("asking for a beer");
    .send("robot@localhost", achieve, has(owner, beer)).

+has(owner,beer) : true
    <- 
    !drink(beer).

-has(owner,beer) : true
    <- 
    .print("I drank the beer, I have no more beers! :(");
    .wait(1000);
    !get(beer).


// drink the beer
+!drink(beer) : has(owner,beer) 
    <- 
    .sip(beer);
    !drink(beer).

+!drink(beer) : not has(owner,beer).


// print received messages
+msg(M)[source(Ag)] : true
    <- 
    .print("Message from ",Ag,": ",M);
    -msg(M).