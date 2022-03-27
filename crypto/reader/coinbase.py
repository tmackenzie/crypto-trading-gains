from decimal import Decimal
import csv
import re
from . import util

# coinbase does this in notes field when crypto/crypto trades
NON_FIAT_EXPR = re.compile("Converted (?P<base_asset_amount>\d+.\d+) (?P<base_asset>\w+) to (?P<quote_asset_amount>\d+.\d+) (?P<quote_asset>\w+)")

def row_to_dict(row):
    hdr = [{"key": "timestamp",
            "type": "datetime"},
           {"key": "transaction_type",
            "type": "string"},
           {"key": "asset",
            "type": "string"},
           {"key": "quantity_transacted",
            "type": "decimal"},
           {"key": "spot_price_currency",
            "type": "string"},
           {"key": "spot_price_at_transaction",
            "type": "decimal"},
           {"key": "subtotal",
            "type": "decimal"},
           {"key": "total_inclusive_of_fees",
            "type": "decimal"},
           {"key": "fees",
            "type": "decimal"},
           {"key": "notes",
            "type": "string"}]

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
    """ read in coinbase files and return data as ledger """
    ledger = []
    deposits = {}
    for file in files:
        with open(file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)

            for row in reader:
                coinbase_trx = row_to_dict(row)

                trx_fn = trx_factory(coinbase_trx)
                trx = trx_fn(coinbase_trx)
                ledger.append(trx)

    return {"deposits": deposits,
            "ledger": ledger}

def trx_factory(coinbase_trx):
    
    if coinbase_trx["transaction_type"] == "Convert":
        return convert
    elif coinbase_trx["transaction_type"] == "Sell":
        return sell
    elif coinbase_trx["transaction_type"] == "Buy" or coinbase_trx["transaction_type"] == "Rewards Income":
        return buy
    elif coinbase_trx["transaction_type"] == "Send" or coinbase_trx["transaction_type"] == "Receive":
        return deposit

def convert(coinbase_trx):
    # sell base, receive quote
    asset_candidate = coinbase_trx["asset"]
    asset = util.CURRENCY.get(asset_candidate, asset_candidate)
    trx_type = util.trx_type(coinbase_trx["transaction_type"])
    timestamp = coinbase_trx["timestamp"]
    epoch_seconds = timestamp.timestamp()
    qty = coinbase_trx["quantity_transacted"]
    
    trade = NON_FIAT_EXPR.search(coinbase_trx["notes"]).groupdict()
    trade["base_asset_amount"] = Decimal(trade["base_asset_amount"])
    trade["quote_asset_amount"] = Decimal(trade["quote_asset_amount"])

    entry = {"timestamp": timestamp,
             "epoch_seconds": epoch_seconds,
             "trx_type": trx_type,
             "qty": coinbase_trx["quantity_transacted"],
             "spot_currency": coinbase_trx["spot_price_currency"],
             "subtotal": coinbase_trx["subtotal"],
             "total": Decimal(coinbase_trx["total_inclusive_of_fees"]),
             "fees": coinbase_trx["fees"],
             "exchange": "coinbase"} | trade

    entry["hash_key"] = util.dict_to_hash_key(entry)

    reference_entry = {"timestamp": timestamp,
                       "epoch_seconds": epoch_seconds,
                       "trx_type": "buy",
                       "ref_hash_key": entry["hash_key"],
                       "qty": trade["base_asset_amount"],
                       "spot_currency": coinbase_trx["spot_price_currency"],
                       "subtotal": coinbase_trx["subtotal"],
                       "total": coinbase_trx["total_inclusive_of_fees"],
                       "fees": coinbase_trx["fees"],
                       "exchange": "coinbase",
                       "available_to_sell": qty,
                       "sales": []} | trade
    
    reference_entry["hash_key"] = util.dict_to_hash_key(reference_entry)

    return entry

def sell(coinbase_trx):
    # sell base, receive quote

    asset_candidate = coinbase_trx["asset"]
    asset = util.CURRENCY.get(asset_candidate, asset_candidate)
    trx_type = util.trx_type(coinbase_trx["transaction_type"])
    timestamp = coinbase_trx["timestamp"]
    epoch_seconds = timestamp.timestamp()

    trade = {"base_asset": asset,
             "base_asset_amount": coinbase_trx["quantity_transacted"],
             "quote_asset": "USD",
             "quote_asset_amount": coinbase_trx["subtotal"]}

    entry = {"timestamp": timestamp,
             "epoch_seconds": epoch_seconds,
             "trx_type": trx_type,
             "qty": coinbase_trx["quantity_transacted"],
             "spot_currency": coinbase_trx["spot_price_currency"],
             "subtotal": coinbase_trx["subtotal"],
             "total": coinbase_trx["total_inclusive_of_fees"],
             "fees": coinbase_trx["fees"],
             "exchange": "coinbase"} | trade
    
    entry["hash_key"] = util.dict_to_hash_key(entry)    
    
    return entry

def buy(coinbase_trx):
    
    asset_candidate = coinbase_trx["asset"]
    asset = util.CURRENCY.get(asset_candidate, asset_candidate)
    trx_type = util.trx_type(coinbase_trx["transaction_type"])
    timestamp = coinbase_trx["timestamp"]
    epoch_seconds = timestamp.timestamp()
    qty = coinbase_trx["quantity_transacted"]

    trade = {"quote_asset": "USD",
             "quote_asset_amount": coinbase_trx["subtotal"],
             "base_asset": asset,
             "base_asset_amount": coinbase_trx["quantity_transacted"]}

    entry = {"timestamp": timestamp,
             "epoch_seconds": epoch_seconds,
             "trx_type": trx_type,
             "qty": qty,
             "spot_currency": coinbase_trx["spot_price_currency"],
             "subtotal": coinbase_trx["subtotal"],
             "total": coinbase_trx["total_inclusive_of_fees"],
             "fees": coinbase_trx["fees"],
             "exchange": "coinbase"} | trade

    entry["hash_key"] = util.dict_to_hash_key(entry)

    return entry

def deposit(coinbase_trx):

    asset_candidate = coinbase_trx["asset"]
    asset = util.CURRENCY.get(asset_candidate, asset_candidate)
    trx_type = util.trx_type(coinbase_trx["transaction_type"])
    timestamp = coinbase_trx["timestamp"]
    epoch_seconds = timestamp.timestamp()

    entry = {"timestamp": timestamp,
             "epoch_seconds": epoch_seconds,
             "trx_type": trx_type,
             "asset": asset,
             "qty": coinbase_trx["quantity_transacted"],
             "subtotal": coinbase_trx["subtotal"],
             "exchange": "coinbase"} 
                    
    entry["hash_key"] = util.dict_to_hash_key(entry)

    return entry