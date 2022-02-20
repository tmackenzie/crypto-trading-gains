from decimal import Decimal
import csv
from . import util


def row_to_dict(row):
    hdr = [{"key": "user_id", "type": "string"},
           {"key": "time", "type": "datetime"},
           {"key": "category", "type": "string"},
           {"key": "operation", "type": "string"},
           {"key": "order_id", "type": "string"},
           {"key": "transaction_id", "type": "string"},
           {"key": "primary_asset", "type": "string"},
           {"key": "realized_amount_for_primary_asset", "type": "decimal"},
           {"key": "realized_amount_for_primary_asset_in_usd_value", "type": "decimal"},
           {"key": "base_asset", "type": "string"},
           {"key": "realized_amount_for_base_asset", "type": "decimal"},
           {"key": "realized_amount_for_base_asset_in_usd_value", "type": "decimal"},
           {"key": "quote_asset", "type": "string"},
           {"key": "realized_amount_for_quote_asset", "type": "decimal"},
           {"key": "realized_amount_for_quote_asset_in_usd_value", "type": "decimal"},
           {"key": "fee_asset", "type": "string"},
           {"key": "realized_amount_for_fee_asset", "type": "decimal"},
           {"key": "realized_amount_for_fee_asset_in_usd_value", "type": "decimal"},
           {"key": "payment_method", "type": "string"},
           {"key": "withdrawal_method", "type": "string"},
           {"key": "additional_note", "type": "string"}]

    trx = {}
    for i in range(0, len(row)):
        expected_type = hdr[i]["type"]
        if expected_type == "decimal" and row[i] == "":
            trx[hdr[i]["key"]] = Decimal(0)
        elif expected_type == "decimal" and row[i] != "":
            trx[hdr[i]["key"]] = Decimal(row[i])
        elif expected_type == "datetime":
            trx[hdr[i]["key"]] = util.to_datetime(row[i])
        else: 
            trx[hdr[i]["key"]] = row[i]

    return trx


def reader(files):

    ledger = {}
    deposits = {}
    for file in files:
        with open(file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)

            for row in reader:
                # base is bought
                # quote is sold
                binance_trx = row_to_dict(row)

                trx_fn = trx_factory(binance_trx)
                trxs = trx_fn(binance_trx)
                
                for asset, trx in trxs.items():
                    if asset in ledger:
                        ledger[asset].append(trx)
                    else:
                        ledger[asset] = [trx]

    
    return {"deposits": deposits,
            "ledger": ledger}


def trx_factory(binance_trx):
    operation = binance_trx["operation"]
    if binance_trx["category"] == "Quick Buy":
        return quick_buy
    elif operation == "Sell" or operation == "Buy":
        return sell_or_buy
    elif operation == "Staking Rewards":
        return staking_rewards
    elif operation == "Crypto Deposit" or operation == "USD Deposit":
        return deposit

def quick_buy(binance_trx):
    # stupid binance - need to invert quote and base
    asset = binance_trx["quote_asset"]
    timestamp = binance_trx["time"]
    epoch_seconds = timestamp.timestamp()
    operation = binance_trx["operation"]
    trx_type = util.trx_type(operation)

    trade = {"base_asset": binance_trx["quote_asset"],
             "base_asset_amount": binance_trx["realized_amount_for_quote_asset"],
             "quote_asset": binance_trx["base_asset"],
             "quote_asset_amount": binance_trx["realized_amount_for_base_asset"]}

    entry = {"timestamp": timestamp,
             "epoch_seconds": epoch_seconds,
             "trx_type": trx_type,
             "qty": binance_trx["realized_amount_for_quote_asset"],
             "spot_currency": binance_trx["quote_asset"],
             "subtotal": binance_trx["realized_amount_for_quote_asset_in_usd_value"],
             "fees": binance_trx["realized_amount_for_fee_asset_in_usd_value"],
             "exchange": "binance"} | trade

    entry["hash_key"] = util.dict_to_hash_key(entry)
    return {asset: entry}

def staking_rewards(binance_trx):
    asset = binance_trx["primary_asset"]
    timestamp = binance_trx["time"]
    epoch_seconds = timestamp.timestamp()
    operation = binance_trx["operation"]
    trx_type = util.trx_type(operation)

    trade = {"base_asset": binance_trx["primary_asset"],
             "base_asset_amount": binance_trx["realized_amount_for_primary_asset"]}

    entry = {"timestamp": timestamp,
             "epoch_seconds": epoch_seconds,
             "trx_type": trx_type,
             "qty": binance_trx["realized_amount_for_primary_asset"],
             "spot_currency": "USD",
             "subtotal": binance_trx["realized_amount_for_primary_asset_in_usd_value"],
             "fees": binance_trx["realized_amount_for_fee_asset_in_usd_value"],
             "exchange": "binance"} | trade

    entry["hash_key"] = util.dict_to_hash_key(entry)
    return {asset: entry}

def sell_or_buy(binance_trx):
    asset = binance_trx["base_asset"]
    timestamp = binance_trx["time"]
    epoch_seconds = timestamp.timestamp()
    operation = binance_trx["operation"]
    trx_type = util.trx_type(operation)

    # base is bought, quote is sold

    trade = {"quote_asset": binance_trx["quote_asset"],
             "quote_asset_amount": binance_trx["realized_amount_for_quote_asset"],
             "base_asset": binance_trx["base_asset"],
             "base_asset_amount": binance_trx["realized_amount_for_base_asset"]}

    entry = {"timestamp": timestamp,
             "epoch_seconds": epoch_seconds,
             "trx_type": trx_type,
             "qty": binance_trx["realized_amount_for_base_asset"],
             "spot_currency": binance_trx["quote_asset"],
             "subtotal": binance_trx["realized_amount_for_quote_asset_in_usd_value"],
             "fees": binance_trx["realized_amount_for_fee_asset_in_usd_value"],
             "exchange": "binance"} | trade

    entry["hash_key"] = util.dict_to_hash_key(entry)
    return {asset: entry}

def deposit(binance_trx):
    asset = binance_trx["primary_asset"]
    timestamp = binance_trx["time"]
    epoch_seconds = timestamp.timestamp()
    operation = binance_trx["operation"]
    trx_type = util.trx_type(operation)

    entry = {"timestamp": timestamp,
             "epoch_seconds": epoch_seconds,
             "trx_type": trx_type,
             "asset": asset,
             "qty": binance_trx["realized_amount_for_primary_asset"],
             "subtotal": binance_trx["realized_amount_for_primary_asset_in_usd_value"],
             "exchange": "binance"}
        
    entry["hash_key"] = util.dict_to_hash_key(entry)

    return {asset: entry}