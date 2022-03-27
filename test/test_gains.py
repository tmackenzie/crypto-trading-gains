from decimal import Decimal
from crypto import gains
import json
import os
import unittest

class TestGains(unittest.TestCase):

    def to_decimal(value, sig_digits):
        return Decimal(value).quantize(sig_digits)

    
    def test_btc_gains(self):
        btc_file_name = os.path.join(os.path.dirname(__file__), "files/btc.json")
        btc_file = open(btc_file_name)
        trxs = json.load(btc_file, parse_float=Decimal)
        btc_file.close()

        btc_trxs = trxs[0:4]
        actual = gains.gains(3, btc_trxs)

        self.assertEqual(actual[3]["qty_reconciled"], Decimal(0.991649).quantize(Decimal('0.000001')))
        self.assertEqual(actual[3]["buys"][0]["cost"], Decimal(1))
        self.assertEqual(actual[3]["buys"][1]["cost"].quantize(Decimal('.000001')),
                         Decimal(362.026401).quantize(Decimal('.000001')))

        self.assertEqual(actual[1]["available_to_sell"], Decimal(0.0111).quantize(Decimal('.0001')))
        self.assertEqual(actual[0]["available_to_sell"], Decimal(0))

        self.assertEqual(actual[3]["profit"], Decimal(623.663599).quantize(Decimal('.000001')))
        self.assertEqual(actual[3]["cost_basis"], Decimal(363.026401).quantize(Decimal('.000001')))

    def test_crypto_pairs_gains(self):
        btc_file_name = os.path.join(os.path.dirname(__file__), "files/btc.json")
        btc_file = open(btc_file_name)
        trxs = json.load(btc_file, parse_float=Decimal)
        btc_file.close()

        btc_trxs = trxs[0:10]
        gains.gains(3, btc_trxs) # first time to calc sell

        actual = gains.gains(9, btc_trxs)

        self.assertEqual(actual[9]["qty_reconciled"].quantize(Decimal('0.000001')),
                         Decimal(0.017906).quantize(Decimal('0.000001')))

        self.assertEqual(actual[9]["buys"][0]["cost"].quantize(Decimal('0.000001')),
                         Decimal(4.06359900).quantize(Decimal('0.000001')))

        self.assertEqual(actual[9]["buys"][1]["cost"].quantize(Decimal('.000001')),
                         Decimal(43.384549).quantize(Decimal('.000001')))

        self.assertEqual(actual[9]["profit"].quantize(Decimal('.000001')),
                         Decimal(982.401852).quantize(Decimal('.000001')))

        self.assertEqual(actual[9]["cost_basis"].quantize(Decimal('.000001')), 
                         Decimal(47.448148).quantize(Decimal('.000001')))

    def test_qtum_gains(self):
        qtum_file_name = os.path.join(os.path.dirname(__file__), "files/qtum.json")
        qtum_file = open(qtum_file_name)
        trxs = json.load(qtum_file, parse_float=Decimal)
        qtum_file.close()

        qtum_trxs = trxs[0:8]
        
        actual = gains.gains(7, qtum_trxs)

        self.assertEqual(actual[7]["qty_reconciled"], Decimal('34.513').quantize(Decimal('0.001')))

        self.assertEqual(actual[7]["profit"].quantize(Decimal('.000001')),
                         Decimal(-504.804145).quantize(Decimal('.000001')))

        self.assertEqual(actual[7]["cost_basis"].quantize(Decimal('.000001')),
                         Decimal(1059.013899374783801551992946).quantize(Decimal('.000001')))


if __name__ == '__main__':
    unittest.main()
