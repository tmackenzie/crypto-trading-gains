# Reader

Trading history can be read from `coinbase` and `binance`. 

Source data is translated to the following transacton types:
 - sell
 - buy
 - staking
 - rewards income
 - send
 - receive

A `sell` transaction results in giving the `base_asset` and receiving the `quote_asset`.

A `sell` example is giving LINK (base_asset) and receiving USD (quote_asset).

A `buy` transation results in receiving the `base_asset` and giving the `quote_asset`.

A `buy` example is recieving LINK (base_asset) and giving USD (quote_asset).


