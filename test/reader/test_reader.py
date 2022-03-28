from decimal import Decimal
from crypto.reader import reader
import os
import unittest


class TestReader(unittest.TestCase):

    def test_reader(self):
        binance_file_name = os.path.join(os.path.dirname(__file__), "../files/binance.csv")
        coinbase_file_name = os.path.join(os.path.dirname(__file__), "../files/cb.csv")

        trxs = reader.read([coinbase_file_name], [binance_file_name])
        
        self.assertEqual(94, len(trxs["ledger"]))

        # make sure its sorted by epoch_seconds.
        prev = {"epoch_seconds": 0} # dummy entry for first comparison
        for trx in trxs["ledger"]:
            self.assertTrue(prev["epoch_seconds"] <= trx["epoch_seconds"], "transactions are not sorted by epoch_seconds")
            prev = trx