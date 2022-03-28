#!/usr/bin/env python

from . import util

def earnings(trxs, start_date, end_date):
    start_epoch = start_date.timestamp()
    end_epoch = end_date.timestamp()

    short_term_earnings = 0
    long_term_earnings = 0
    fees = 0

    sells = []
    for i in range(0, len(trxs)):
        in_between = util.date_is_between(start_epoch, end_epoch, trxs[i]["epoch_seconds"])

        if trxs[i]["trx_type"] == "sell" and in_between:
            fees += trxs[i]["fees"]
            sells.append(trxs[i])

            earnings = sale_earnings(trxs[i]["buys"])
            trxs[i].update(earnings)

            short_term_earnings += earnings["short_term"]
            long_term_earnings += earnings["long_term"]

        elif trxs[i]["trx_type"] == "rewards income" and in_between:
            sells.append(trxs[i])
            short_term_earnings += trxs[i]["qty"]
    
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
    
    return {"short_term": short_term_earnings,
            "long_term": long_term_earnings}