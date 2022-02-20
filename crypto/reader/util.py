from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json

CURRENCY = {"USDC": "USD"}
TRX_TYPES = {"Crypto Deposit": "Receive", "USD Deposit": "Receive", "Convert": "Sell"}

def trx_type(source_type):
    trx_type = TRX_TYPES.get(source_type, source_type)
    return trx_type.lower()

def deepupdate(original, update):
    """
    Recursively update a dict of deposits and ledgers
    """
    for key, value in original.items(): 
        if key not in update:
            update[key] = value
        elif isinstance(value, list):
            update[key] = sorted(update[key] + value, key = lambda d: d['epoch_seconds'])
        elif isinstance(value, dict):
            deepupdate(value, update[key]) 
    return update


def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return str(obj)
    raise TypeError ("Type %s not serializable" % type(obj))

def dict_to_hash_key(entry):
    entry_encoded = json.dumps(entry, sort_keys=True, default=json_serializer).encode()
    hasher = hashlib.sha512()
    hasher.update(entry_encoded)
    return hasher.hexdigest()

def to_datetime(input):
    input_candidate = input.replace('Z','')
    input_dt = datetime.fromisoformat(input_candidate).replace(tzinfo=timezone.utc)
    return input_dt