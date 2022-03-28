#!/usr/bin/env python

import argparse
import csv
from gain import gain, earning, deposit
import json
from reader import reader
from reader import util



def main():
    parser = argparse.ArgumentParser(description='Crypto Gains')
    parser.add_argument('--b', metavar='file from binance', nargs='?', action='append', dest='binance_files', help='file from binance')
    parser.add_argument('--c', metavar='file from coinbase', nargs='?', action='append', dest='coinbase_files', help='file from coinbase')

    parser.add_argument('--s', metavar='start date to calculate gains and taxes', dest='input_start_date', help='YYYY-MM-DD', required=True)
    parser.add_argument('--e', metavar='end date to calculate gains and taxes', dest='input_end_date', help='YYYY-MM-DD', required=True)
    
    parser.add_argument('--o', metavar='output file in json', dest='outfile_name', default='transactions.json', help='output file name for all transactions read from source (nearly unmodified), JSON formatted')
    parser.add_argument('--g', metavar='gains output file in json', dest='gains_outfile_name', default='gains.json', help='output file name for all gains and losses, filtered by date range. JSON formatted')
    parser.add_argument('--t', metavar='tax output file in csv', dest='tax_outfile_name', default='tax.csv', help='output file name for transactions to report taxes')
    parser.add_argument('--d', metavar='usd deposits output file in json', dest='deposit_outfile_name', default='deposits.json', help='USD deposits output file name in json')

    args = parser.parse_args()
    financials = reader.read(args.coinbase_files, args.binance_files)
    write_json_file(args.outfile_name, financials) # financials get modified somewhere by reference.

    ledger = gain.accumulated_amounts(financials["ledger"])

    start_date = util.to_datetime(args.input_start_date)
    end_date = util.to_datetime(args.input_end_date)

    sell_trxs = earning.earnings(ledger, start_date, end_date)
    deposits = deposit.usd_deposits(ledger, start_date, end_date)
    
    write_json_file(args.gains_outfile_name, sell_trxs)
    write_json_file(args.deposit_outfile_name, deposits)

    with open(args.tax_outfile_name, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'hash_key', 'trx_type', 'base_asset', 'quote_asset', 'qty', 'subtotal', 'fees', 'profit', 'cost_basis', 'short_term', 'long_term']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for sale in sell_trxs["transactions"]:
            missing = set(fieldnames) - sale.keys()
            row_missing = {key: "missing" for key in missing}
            sale.update(row_missing)
            row = {key: sale[key] for key in fieldnames}
            writer.writerow(row)

def write_json_file(filename, data):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True, default=util.json_serializer)

if __name__ == '__main__':
    main();
