# Crypto-Trading-Gains
Calculate capital gains for crypto trades


## General

This will calculate amount owed for US taxes for crypto trading.


## Usage

```bash
$ python3 --c coinbase.csv --b binance.csv --s 2021-01-01 --e 2021-12-31
```

This will output the following files:
 - `transactions.json`: all transactions read from cb or binance into a common interface.
 - `gains.json`: all the sell transactions filtered by inputed date with PnL
 - `deposits.json`: all USD deposits filtered by inputed date
 - `tax.csv`: data showing sell transactions with profit, cost basis, short term and long term earnings.

 ## More Documentation

More documentation about how this all works is [available](/docs/README.md).
