from decimal import Decimal
from crypto.reader import coinbase
import json
import os
import unittest

class TestCoinbaseReader(unittest.TestCase):

    def test_coinbase_reader(self):
        coinbase_file_name = os.path.join(os.path.dirname(__file__), "../files/cb.csv")

        trxs = coinbase.reader([coinbase_file_name])
        
        self.assertEqual(56, len(trxs["ledger"]))

        sells, buys, deposits, withdrawl = 0, 0, 0, 0

        # verify interface for each transaction type
        for trx in trxs["ledger"]:
            if trx["trx_type"] == "sell":
                self.assert_sell(trx)
                sells = sells + 1
            elif trx["trx_type"] in {"buy", "rewards income"}:
                self.assert_buy(trx)
                buys = buys + 1
            elif trx["trx_type"] == "receive":
                self.assert_deposit(trx)
                deposits = deposits + 1
            elif trx["trx_type"] == "send":
                self.assert_withdrawl(trx)
                withdrawl = withdrawl + 1
            else:
                self.fail("unknown transaction type {}".format(trx["trx_type"]))

        self.assertEqual(6, sells, "number of sells are incorrect")
        self.assertEqual(36, buys, "number of buys are incorrect")
        self.assertEqual(5, deposits, "number of deposits are incorrect")
        self.assertEqual(9, withdrawl, "number of withdrawls are incorrect")

    def assert_buy(self, buy):
        buy_keys = {"quote_asset", "quote_asset_amount", "base_asset", "base_asset_amount",
                    "timestamp", "epoch_seconds", "trx_type", "qty", "spot_currency",
                    "subtotal", "total", "fees", "exchange", "hash_key",
                    "give", "receive"}

        self.assertTrue(buy.keys() == buy_keys, "failed buy interface check: {}".format(buy.keys()))

    def assert_sell(self, sell):
        sell_keys = {"quote_asset", "quote_asset_amount", "base_asset", "base_asset_amount",
                     "timestamp", "epoch_seconds", "trx_type", "qty", "spot_currency",
                     "subtotal", "total", "fees", "exchange", "hash_key",
                     "give", "receive"}

        self.assertTrue(sell.keys() == sell_keys, "failed sell interface check: {}".format(sell.keys()))

    def assert_deposit(self, deposit):
        deposit_keys = {"timestamp", "epoch_seconds", "trx_type", "asset", 
                        "qty", "subtotal", "exchange", "hash_key", "receive"}

        self.assertTrue(deposit.keys() == deposit_keys, "failed deposit interface check: {}".format(deposit.keys()))
    
    def assert_withdrawl(self, deposit):
        deposit_keys = {"timestamp", "epoch_seconds", "trx_type", "asset", 
                        "qty", "subtotal", "exchange", "hash_key", "give"}

        self.assertTrue(deposit.keys() == deposit_keys, "failed withdrawl interface check: {}".format(deposit.keys()))