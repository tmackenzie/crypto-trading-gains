#!/usr/bin/env python

from decimal import Decimal
from functools import reduce


BUY = {"buy", "staking rewards", "rewards income"}
SELL = {"sell", "send"}
YEAR_IN_SECONDS = 31556926

def accumulated_amounts(trxs):
    trx_acc = trxs

    for key, value in trx_acc.items():
        acc_amount = Decimal(0)
        for i in range(0, len(value)):
            if value[i]["trx_type"] in BUY:
                value[i]["sales"] = []
                qty = "base_asset_amount" if "base_asset_amount" in value[i] else "qty"
                value[i]["available_to_sell"] = value[i][qty]
                acc_amount += value[i][qty]
            elif value[i]["trx_type"] in SELL:
                value[i]["qty_reconciled"] = Decimal(0)
                value[i]["buys"] = []
                acc_amount -= value[i]["qty"]

            value[i]["qty_acc"] = acc_amount

            if value[i]["trx_type"] == "sell":
                gains(i, value)

    return trx_acc

def is_buy(trx):
    return trx["trx_type"] in BUY and "available_to_sell" in trx and trx["available_to_sell"] > Decimal("0")

def gains(sell_index, trxs):
    """ look back and see what has been gained from a sell """
    
    sale = trxs[sell_index]

    for i in range(0, sell_index+1):

        if sale["qty_reconciled"] >= sale["qty"]:
            break

        if is_buy(trxs[i]):
            remaining_to_fill = sale["qty"] if sale["qty_reconciled"] == Decimal(0) else sale["qty"] - sale["qty_reconciled"]
            if remaining_to_fill > trxs[i]["available_to_sell"]:
                qty_taken = trxs[i]["available_to_sell"]
                trxs[i]["available_to_sell"] = Decimal(0)
            else:
                qty_taken = remaining_to_fill
                trxs[i]["available_to_sell"] -= remaining_to_fill

            sale_entry = {"ref_hash_key": sale["hash_key"]}
            trxs[i]["sales"].append(sale_entry)

            
            buy_price_per_coin = trxs[i]["subtotal"] / trxs[i]["base_asset_amount"]
            sale_price_per_coin = sale["subtotal"] / sale["quote_asset_amount"]
            cost = qty_taken * buy_price_per_coin
            profit = (qty_taken * sale_price_per_coin) - cost

            tax_category = "short" if sale["epoch_seconds"] - trxs[i]["epoch_seconds"] <= YEAR_IN_SECONDS else "long"
            buy = {"timestamp": trxs[i]["timestamp"],
                   "epoch_seconds": trxs[i]["epoch_seconds"],
                   "qty": qty_taken,
                   "ref_hash_key": trxs[i]["hash_key"],
                   "cost": cost,
                   "buy_price_per_coin": buy_price_per_coin,
                   "sale_price_per_coin": sale_price_per_coin,
                   "profit": profit,
                   "capital_gains_category": tax_category}

            sale["buys"].append(buy)
            sale["qty_reconciled"] = qty_taken + sale["qty_reconciled"]

    return trxs
    

def date_is_between(start_epoch, end_epoch, input_epoch):
    return (input_epoch >= start_epoch and input_epoch <= end_epoch)

def usd_deposits(trxs, start_date, end_date):
    start_epoch = start_date.timestamp()
    end_epoch = end_date.timestamp()

    total = 0
    deposits = []
    for i in range(0, len(trxs["USD"])):
        trx = trxs["USD"][i]
        if trx["trx_type"] == "receive" and date_is_between(start_epoch, end_epoch, trx["epoch_seconds"]):
            deposits.append(trx)
            total += trx["qty"]
    
    summary = {"total": total}
    return {"summary": summary} | {"transactions": deposits}

def earnings(trxs, start_date, end_date):
    start_epoch = start_date.timestamp()
    end_epoch = end_date.timestamp()

    short_term_earnings = 0
    long_term_earnings = 0
    fees = 0

    sells = []
    for key,value in trxs.items():
        for i in range(0, len(value)):
            in_between = date_is_between(start_epoch, end_epoch, value[i]["epoch_seconds"])

            if value[i]["trx_type"] == "sell" and in_between:
                fees += value[i]["fees"]
                sells.append(value[i])

                earnings = sale_earnings(value[i]["buys"])
                short_term_earnings += earnings["short_term"]
                long_term_earnings += earnings["long_term"]

            elif value[i]["trx_type"] == "rewards income" and in_between:
                sells.append(value[i])
                short_term_earnings += value[i]["qty"]
    
    summary = {"earnings": {"fees": fees,
                            "long_term": long_term_earnings,
                            "short_term": short_term_earnings,
                            "subtotal": long_term_earnings + short_term_earnings},
               "trx_count": len(sells)}

    return {"summary": summary} | {"transactions": sells}

def sale_earnings(buys):
    short_term_earnings = 0
    long_term_earnings = 0

    for buy in buys:
        if buy["capital_gains_category"] == "short":
            short_term_earnings += buy["profit"]
        elif buy["capital_gains_category"] == "long":
            long_term_earnings += buy["profit"]
    
    return {"short_term":  short_term_earnings,
            "long_term": long_term_earnings}