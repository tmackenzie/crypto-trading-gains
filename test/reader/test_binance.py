from decimal import Decimal
from crypto.reader import binance
import os
import unittest

class TestBinanceReader(unittest.TestCase):

    def test_coinbase_reader(self):
        binance_file_name = os.path.join(os.path.dirname(__file__), "../files/binance.csv")

        trxs = binance.reader([binance_file_name])
        
        self.assertEqual(38, len(trxs["ledger"]))

        sells, buys, stakings, deposits, withdrawl = 0, 0, 0, 0, 0
        # verify interface for each transaction type
        for trx in trxs["ledger"]:
            if trx["trx_type"] == "sell":
                self.assert_sell(trx)
                sells = sells + 1
            elif trx["trx_type"] == "buy":
                self.assert_buy(trx)
                buys = buys + 1
            elif trx["trx_type"] == "staking rewards":
                self.assert_staking(trx)
                stakings = stakings + 1
            elif trx["trx_type"] in {"send", "receive"}:
                self.assert_deposit(trx)
                deposits = deposits + 1
            elif trx["trx_type"] == "send":
                self.assert_withdrawl(trx)
                withdrawl = withdrawl + 1
            else:
                self.fail("unknown transaction type {}".format(trx["trx_type"]))

        self.assertEqual(1, sells, "number of sells are incorrect")
        self.assertEqual(16, buys, "number of buys are incorrect")
        self.assertEqual(7, stakings, "number of stakings are incorrect")
        self.assertEqual(14, deposits, "number of deposits are incorrect")
        self.assertEqual(0, withdrawl, "number of withdrawls are incorrect")

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


    def assert_staking(self, staking):
        sell_keys = {"base_asset", "base_asset_amount",
                     "timestamp", "epoch_seconds", "trx_type", "qty", "spot_currency",
                     "subtotal", "total", "fees", "exchange", "hash_key", "receive"}

        self.assertTrue(staking.keys() == sell_keys, "failed staking interface check: {}".format(staking.keys()))

    def assert_deposit(self, deposit):
        deposit_keys = {"timestamp", "epoch_seconds", "trx_type", "asset", 
                        "qty", "subtotal", "exchange", "hash_key", "receive"}

        self.assertTrue(deposit.keys() == deposit_keys, "failed deposit interface check: {}".format(deposit.keys()))

    def assert_withdrawl(self, deposit):
        deposit_keys = {"timestamp", "epoch_seconds", "trx_type", "asset", 
                        "qty", "subtotal", "exchange", "hash_key", "give"}

        self.assertTrue(deposit.keys() == deposit_keys, "failed withdrawl interface check: {}".format(deposit.keys()))