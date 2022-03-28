#!/usr/bin/env python

from decimal import Decimal
from functools import reduce
from . import util

def usd_deposits(trxs, start_date, end_date):
    start_epoch = start_date.timestamp()
    end_epoch = end_date.timestamp()

    total = 0
    deposits = []

    for trx in trxs:
        if trx["trx_type"] == "receive" and util.date_is_between(start_epoch, end_epoch, trx["epoch_seconds"]) and trx["receive"] == "USD":
            deposits.append(trx)
            total += trx["qty"]
    
    summary = {"total": total}
    return {"summary": summary} | {"transactions": deposits}