start.

+start
<-
    .print("Hello, world!");
    .at(2, "+say('hello','world')");
    .at(2, "+say('hello')");
    .at(3, "+!run('rudolf')");
    .at(4, "-say('hello','world')");
    .at(4, "-!run('rudolf')").

 
+say(M)
<-
    .print("saying just", M).

+say(M,Who)
<-
    .print("I've said", M, Who).

-say(M,Who)
<-
    .print("I said nothing. Forget", M).

+!run(Who)
<-
    .print("Run,",Who,", run").

-!run(Who)
<-
    .print("Forget about running". Who).