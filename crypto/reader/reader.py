#!/usr/bin/env python

from . import binance
from . import coinbase
from . import util


def read(coinbase_files, binance_files):
    """
    Reads in files from coinbase and binance.
    Converts them to common interface
    Returns the data sorted by date
    """
    cb_financials = coinbase.reader(coinbase_files)
    binance_financials = binance.reader(binance_files)

    return util.deepupdate(cb_financials, binance_financials)
