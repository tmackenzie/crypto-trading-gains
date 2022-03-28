#!/usr/bin/env python

from decimal import Decimal
from functools import reduce
from . import util


BUY = {"buy", "staking rewards", "rewards income"}
SELL = {"sell", "send"}
YEAR_IN_SECONDS = 31556926
FIAT = {"USD"}

# helper fns to improve readability b/c fn name is descriptive.

def is_buy(trx, sale_asset):
    ''' is trx a buy transaction and can it be processed? '''
    return trx["trx_type"] in BUY and trx["available_to_sell"] > Decimal("0") and trx["receive"] == sale_asset

def is_crypto_pairs(trx, sale_asset):
    ''' is this transacton a crytpo/crypto trade and can it be processed? '''
    return trx["trx_type"] == "sell" and trx["give"] not in FIAT and trx["receive"] == sale_asset

def add_keys_to_crypto(trx, sale_asset):
    ''' add available to sell for crypto/crypto trades '''
    
    if is_crypto_pairs(trx, sale_asset):
        trx["available_to_sell"] = trx["quote_asset_amount"]
        trx["sales"] = []

    return trx

def add_keys_to_sale(sale):
    sale["qty_reconciled"] = Decimal(0)
    sale["buys"] = []
    return sale

def add_keys_to_buy(buy):
    
    # ensure available to sell is there for BUYS.
    if buy["trx_type"] in BUY and "available_to_sell" not in buy:
        buy["available_to_sell"] = buy["qty"]
    
    if buy["trx_type"] in BUY:
        buy["sales"] = []

    return buy

# end helper fns


def accumulated_amounts(trxs):
    trx_acc = trxs

    acc_amounts = {}
    for i in range(0, len(trxs)):
        
        asset = ""
        if trxs[i]["trx_type"] in BUY:
            qty = "base_asset_amount" if "base_asset_amount" in trxs[i] else "qty"
            asset = trxs[i]["receive"]
            curr_amount = acc_amounts.get(asset, Decimal(0))
            acc_amounts[asset] = curr_amount + trxs[i][qty]
        elif trxs[i]["trx_type"] in SELL:
            asset = trxs[i]["give"]
            curr_amount = acc_amounts.get(asset, Decimal(0))
            acc_amounts[asset] = curr_amount - trxs[i]["qty"]

        if asset != "":
            trxs[i]["qty_acc"] = acc_amounts[asset]

        if trxs[i]["trx_type"] == "sell":
            gains(i, trxs)

    return trx_acc

def gains_factory(trx, sale_asset):
    ''' returns a fn that will calculate gains given a trx and a sale_asset '''
    
    if is_buy(trx, sale_asset):
        return gains_for_buy
    elif is_crypto_pairs(trx, sale_asset):
        return gains_for_crypto
    else:
        return gains_noop

def gains(sell_index, trxs):
    ''' look back and see what has been gained from a sell '''
    
    sale = trxs[sell_index]
    sale = add_keys_to_sale(sale)

    for i in range(0, sell_index+1):

        if sale["qty_reconciled"] >= sale["qty"]:
            sale["profit"] = reduce(lambda acc, buy: acc + buy["profit"], sale["buys"], 0)
            sale["cost_basis"] = reduce(lambda acc, buy: acc + buy["cost"], sale["buys"], 0)
            break

        trxs[i] = add_keys_to_buy(trxs[i])
        trxs[i] = add_keys_to_crypto(trxs[i], sale["give"])

        gain_fn = gains_factory(trxs[i], sale["give"])
        gains = gain_fn(trxs[i], sale)
        trxs[i] = gains["buy"]
        sale = gains["sale"]
       
    return trxs
    
def gains_for_buy(buy, sale):
    ''' Calculates the gains for a buy and sale transaction that is not crypto/crypto pairs '''

    remaining_to_fill = sale["qty"] if sale["qty_reconciled"] == Decimal(0) else sale["qty"] - sale["qty_reconciled"]
    if remaining_to_fill > buy["available_to_sell"]:
        qty_taken = buy["available_to_sell"]
        buy["available_to_sell"] = Decimal(0)
    else:
        qty_taken = remaining_to_fill
        buy["available_to_sell"] -= remaining_to_fill

    sale_entry = {"ref_hash_key": sale["hash_key"]}
    buy["sales"].append(sale_entry)

    buy_price_per_coin = buy["subtotal"] / buy["base_asset_amount"]

    sale_price_per_coin = sale["subtotal"] / sale["base_asset_amount"]
    cost = qty_taken * buy_price_per_coin
    profit = (qty_taken * sale_price_per_coin) - cost

    tax_category = "short" if sale["epoch_seconds"] - buy["epoch_seconds"] <= YEAR_IN_SECONDS else "long"

    embedded_buy = {"timestamp": buy["timestamp"],
                    "epoch_seconds": buy["epoch_seconds"],
                    "qty": qty_taken,
                    "ref_hash_key": buy["hash_key"],
                    "cost": cost,
                    "buy_price_per_coin": buy_price_per_coin,
                    "sale_price_per_coin": sale_price_per_coin,
                    "profit": profit,
                    "capital_gains_category": tax_category}

    sale["buys"].append(embedded_buy)

    sale["qty_reconciled"] = qty_taken + sale["qty_reconciled"]

    return {"sale": sale, "buy": buy}

def gains_for_crypto(buy, sale):
    ''' Calculates the gains for a buy and sale transaction that is crypto/crypto pairs '''
    
    remaining_to_fill = sale["qty"] if sale["qty_reconciled"] == Decimal(0) else sale["qty"] - sale["qty_reconciled"]
    if remaining_to_fill > buy["available_to_sell"]:
        qty_taken = buy["available_to_sell"]
        buy["available_to_sell"] = Decimal(0)
    else:
        qty_taken = remaining_to_fill
        buy["available_to_sell"] -= remaining_to_fill

    sale_entry = {"ref_hash_key": sale["hash_key"]}
    buy["sales"].append(sale_entry)

    buy_price_per_coin = buy["subtotal"] / buy["quote_asset_amount"]
    # 1029.85 / 907.08530165

    sale_price_per_coin = sale["subtotal"] / sale["base_asset_amount"]
    cost = qty_taken * buy_price_per_coin
    profit = (qty_taken * sale_price_per_coin) - cost

    tax_category = "short" if sale["epoch_seconds"] - buy["epoch_seconds"] <= YEAR_IN_SECONDS else "long"

    embedded_buy = {"timestamp": buy["timestamp"],
                    "epoch_seconds": buy["epoch_seconds"],
                    "qty": qty_taken,
                    "ref_hash_key": buy["hash_key"],
                    "cost": cost,
                    "buy_price_per_coin": buy_price_per_coin,
                    "sale_price_per_coin": sale_price_per_coin,
                    "profit": profit,
                    "capital_gains_category": tax_category}

    sale["buys"].append(embedded_buy)

    sale["qty_reconciled"] = qty_taken + sale["qty_reconciled"]

    return {"sale": sale, "buy": buy}

def gains_noop(buy, sale):
    ''' no operation gains '''
    return {"sale": sale, "buy": buy}