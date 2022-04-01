from decimal import Decimal
from crypto.gain import gain
import json
import os
import unittest

class TestGain(unittest.TestCase):

    def to_decimal(value, sig_digits):
        return Decimal(value).quantize(sig_digits)

    
    def test_btc_gains(self):
        btc_file_name = os.path.join(os.path.dirname(__file__), "../files/btc.json")
        btc_file = open(btc_file_name)
        trxs = json.load(btc_file, parse_float=Decimal)
        btc_file.close()

        btc_trxs = trxs[0:4]
        actual_trxs = gain.gains(3, btc_trxs)
        actual = actual_trxs[3]

        self.assertEqual(actual["trx_type"], "sell")
        self.assertEqual(actual["qty_reconciled"], Decimal(0.991649).quantize(Decimal('0.000001')))
        self.assertEqual(actual["buys"][0]["cost"], Decimal(1))
        self.assertEqual(actual["buys"][1]["cost"].quantize(Decimal('.000001')),
                         Decimal(362.026401).quantize(Decimal('.000001')))

        self.assertEqual(actual_trxs[0]["available_to_sell"], Decimal(0))
        self.assertEqual(actual_trxs[1]["available_to_sell"], Decimal(0.0111).quantize(Decimal('.0001')))

        self.assertEqual(actual["profit"], Decimal(623.663599).quantize(Decimal('.000001')))
        self.assertEqual(actual["cost_basis"], Decimal(363.026401).quantize(Decimal('.000001')))

        self.assert_sell_interface(actual)
        self.assert_send_interface(actual_trxs[2])
        self.assert_buy_interface(actual_trxs[1])

    def test_crypto_pairs_gains(self):
        btc_file_name = os.path.join(os.path.dirname(__file__), "../files/btc.json")
        btc_file = open(btc_file_name)
        trxs = json.load(btc_file, parse_float=Decimal)
        btc_file.close()

        btc_trxs = trxs[0:10]
        gain.gains(3, btc_trxs) # first time to calc sell

        actual_trxs = gain.gains(9, btc_trxs)
        actual = actual_trxs[9]

        self.assertEqual(actual["trx_type"], "sell")
        self.assertEqual(actual["qty_reconciled"].quantize(Decimal('0.000001')),
                         Decimal(0.017906).quantize(Decimal('0.000001')))

        self.assertEqual(actual["buys"][0]["cost"].quantize(Decimal('0.000001')),
                         Decimal(4.06359900).quantize(Decimal('0.000001')))

        self.assertEqual(actual["buys"][1]["cost"].quantize(Decimal('.000001')),
                         Decimal(43.384549).quantize(Decimal('.000001')))

        self.assertEqual(actual["profit"].quantize(Decimal('.000001')),
                         Decimal(982.401852).quantize(Decimal('.000001')))

        self.assertEqual(actual["cost_basis"].quantize(Decimal('.000001')), 
                         Decimal(47.448148).quantize(Decimal('.000001')))

        self.assert_sell_interface(actual)
        self.assert_receive_interface(actual_trxs[8])

    def test_qtum_gains(self):
        qtum_file_name = os.path.join(os.path.dirname(__file__), "../files/qtum.json")
        qtum_file = open(qtum_file_name)
        trxs = json.load(qtum_file, parse_float=Decimal)
        qtum_file.close()

        qtum_trxs = trxs[0:8]
        
        actual_trxs = gain.gains(7, qtum_trxs)
        actual = actual_trxs[7]

        self.assertEqual(actual["trx_type"], "sell")
        self.assertEqual(actual["qty_reconciled"], Decimal('34.513').quantize(Decimal('0.001')))

        self.assertEqual(actual["profit"].quantize(Decimal('.000001')),
                         Decimal(-504.804145).quantize(Decimal('.000001')))

        self.assertEqual(actual["cost_basis"].quantize(Decimal('.000001')),
                         Decimal(1059.013899374783801551992946).quantize(Decimal('.000001')))

        self.assert_sell_interface(actual)
        self.assert_staking_interface(actual_trxs[6])


    # helpers to assert interfaces for different transaction types
    def assert_buy_interface(self, buy):
        expected_keys = {"quote_asset", "quote_asset_amount", "base_asset", "base_asset_amount",
                         "timestamp", "epoch_seconds", "trx_type", "qty", "spot_currency",
                         "subtotal", "total", "fees", "exchange", "hash_key",
                         "give", "receive", "available_to_sell", "sales"}

        missing = {}
        desc = ""
        actual = True
        if (len(buy.keys()) > len(expected_keys)):
            actual = False
            missing = buy.keys() - expected_keys
            desc = "failed buy interface check. Extra fields in transaction: {}".format(missing)
        elif (len(buy.keys()) < len(expected_keys)):
            actual = False
            missing = buy - expected_keys.keys()
            desc = "failed buy interface check. Transaction missing keys: {}".format(missing)

        self.assertTrue(actual, desc)

    def assert_sell_interface(self, sell):
        sell_keys = {"quote_asset", "quote_asset_amount", "base_asset", "base_asset_amount",
                     "timestamp", "epoch_seconds", "trx_type", "qty", "spot_currency",
                     "subtotal", "total", "fees", "exchange", "hash_key",
                     "give", "receive", "qty_reconciled", "buys", "profit", "cost_basis"}

        missing = {}
        desc = ""
        actual = True
        if (len(sell.keys()) > len(sell_keys)):
            actual = False
            missing = sell.keys() - sell_keys
            desc = "failed sell interface check. Extra fields in transaction: {}".format(missing)
        elif (len(sell.keys()) < len(sell_keys)):
            actual = False
            missing = sell_keys - sell.keys()
            desc = "failed sell interface check. Transaction missing keys: {}".format(missing)

        self.assertTrue(actual, desc)


    def assert_staking_interface(self, staking):
        expected_keys = {"base_asset", "base_asset_amount",
                         "timestamp", "epoch_seconds", "trx_type", "qty", "spot_currency",
                         "subtotal", "total", "fees", "exchange", "hash_key", "receive"}

        missing = {}
        desc = ""
        actual = True
        if (len(staking.keys()) > len(expected_keys)):
            actual = False
            missing = staking.keys() - expected_keys
            desc = "failed staking interface check. Extra fields in transaction: {}".format(missing)
        elif (len(staking.keys()) < len(expected_keys)):
            actual = False
            missing = expected_keys - staking.keys()
            desc = "failed staking interface check. Transaction missing keys: {}".format(missing)

        self.assertTrue(actual, desc)

    def assert_receive_interface(self, deposit):
        expected_keys = {"timestamp", "epoch_seconds", "trx_type", "asset", 
                         "qty", "subtotal", "exchange", "hash_key", "receive"}

        missing = {}
        desc = ""
        actual = True
        if (len(deposit.keys()) > len(expected_keys)):
            actual = False
            missing = deposit.keys() - expected_keys
            desc = "failed receive interface check. Extra fields in transaction: {}".format(missing)
        elif (len(deposit.keys()) < len(expected_keys)):
            actual = False
            missing = expected_keys - deposit.keys()
            desc = "failed receive interface check. Transaction missing keys: {}".format(missing)

        self.assertTrue(actual, desc)

    def assert_send_interface(self, withdrawl):
        expected_keys = {"timestamp", "epoch_seconds", "trx_type", "asset", 
                        "qty", "subtotal", "exchange", "hash_key", "give"}

        missing = {}
        desc = ""
        actual = True
        if (len(withdrawl.keys()) > len(expected_keys)):
            actual = False
            missing = withdrawl.keys() - expected_keys
            desc = "failed withdrawl interface check. Extra fields in transaction: {}".format(missing)
        elif (len(withdrawl.keys()) < len(expected_keys)):
            actual = False
            missing = expected_keys - withdrawl.keys()
            desc = "failed withdrawl interface check. Transaction missing keys: {}".format(missing)

        self.assertTrue(actual, desc)

if __name__ == '__main__':
    unittest.main()
