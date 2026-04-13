/* Initial beliefs */
last_order_id(0).

/* Set of plans */

+!order(Product,Qtd)[source(Ag)]
    <-
    .print("order received from",Ag, "asking for", Qtd, Product);
    ?last_order_id(N);
    OrderId = N + 1;
    -last_order_id(_);
    +last_order_id(OrderId);
    .deliver(Product,Qtd);
    .send(Ag, tell, delivered(Product,Qtd,OrderId)).

+!order(Product) <-
    .print("I don't know how to order", Product).