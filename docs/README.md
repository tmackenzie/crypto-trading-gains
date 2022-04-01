## Documentation

The application is composed of the following modules
 - [reader](reader.md)
 - [gain](gain.md)

## Transactions

After transactions are read and processed the following fields are avilable.


|Field                    | Description|
|-------------------------|------------|
|`asset`                  | For, send or receive. The currency sent or received.|
|`available_to_sell`      | The quantity available to sell.|
|`base_asset`             | |
|`base_asset_amount`      | |
|`buys`                   | A list of buy transactions that fullfilled a sell transaction.|
|`buy_price_per_coin`     | The price per coin for a buy transaction.|
|`capital_gains_category` | If under a year then, short. if over a year then, long.|
|`cost`                   | Entries in buys or sales will have this field, qty taken * buy price per coin.
|`cost_basis`             | Original value of the currency for transactions that are taxable.|
|`epoch_seconds`          | Transaction date and time in seconds elapsed since UNIX epoch.|
|`exchange`               | Exchange the transaction was executed [binance, coinbase].|
|`fees`                   | Transaction fees.|
|`give`                   | The currency the transaction is giving up.|
|`hash_key`               | Unique identifier for this transaction.|
|`profit`                 | Profit earned for a transaction.|
|`receive`                | The currency the transaction is receiving.|
|`ref_hash_key`           | Entries in buys or sales will have this in order to trace down the referenced transaction.|
|`sales`                  | A list of sales transactions that fullfilled a buy transaction.|
|`sell_price_per_coin`    | The price per coin for a sell transaction.|
|`subtotal`               | Total without fees.|
|`spot_currency`          | |
|`timestamp`              | Transaction date/time in UTC.|
|`total`                  | Total with fees.|
|`trx_type`               | The type of transaction [[buy](#buy), [sell](#sell), [receive](#receive), [send](#send), [rewards income](#rewards-income), [staking rewards](#staking-rewards)].|
|`qty`                    | The quantity the transaction resulted in, bought, sold, received, sent.|
|`qty_reconciled`         | For, sale transactions, the qty fullfilled for a sell transaction.|
|`quote_asset`            | |
|`quote_asset_amount`     | |

### buy

The following field are available to a buy transaction

 * `available_to_sell`
 * `base_asset`
 * `base_asset_amount`
 * `epoch_seconds`
 * `exchange`
 * `fees`
 * `give`
 * `hash_key`
 * `qty`
 * `receive`
 * `sales`
 * `spot_currency`
 * `subtotal`
 * `timestamp`
 * `total`
 * `trx_type`
 * `quote_asset`
 * `quote_asset_amount`

### sell

The following field are available to a sell transaction

 * `base_asset`
 * `base_asset_amount`
 * `buys`
 * `cost_basis`
 * `epoch_seconds`
 * `exchange`
 * `fees`
 * `give`
 * `hash_key`
 * `profit`
 * `qty`
 * `receive`
 * `spot_currency`
 * `subtotal`
 * `timestamp`
 * `total`
 * `trx_type`
 * `qty_acc`
 * `qty_reconciled`
 * `quote_asset`
 * `quote_asset_amount`
 
### receive

The following field are available to a receive transaction

 * `asset`
 * `epoch_seconds`
 * `exchange`
 * `hash_key`
 * `receive`
 * `subtotal` 
 * `timestamp`
 * `trx_type`
 * `qty`

### send

 * `asset`
 * `epoch_seconds`
 * `exchange`
 * `give`
 * `hash_key`
 * `subtotal`
 * `timestamp`
 * `trx_type`
 * `qty`

### rewards income

The following field are available to a rewards incomme transaction

 * `available_to_sell`
 * `base_asset`
 * `base_asset_amount`
 * `epoch_seconds`
 * `exchange`
 * `fees`
 * `give`
 * `hash_key`
 * `qty`
 * `receive`
 * `sales`
 * `spot_currency`
 * `subtotal`
 * `timestamp`
 * `total`
 * `trx_type`
 * `quote_asset`
 * `quote_asset_amount`

### staking rewards

The following field are available to a staking rewards transaction

 * `base_asset`
 * `base_asset_amount`
 * `epoch_seconds`
 * `exchange`
 * `fees`
 * `hash_key`
 * `receive`
 * `subtotal`
 * `timestamp`
 * `total`   
 * `trx_type`
 * `qty`