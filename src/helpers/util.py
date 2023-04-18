
from datetime import datetime

def get_unix_epoch_time_ms(dt: datetime = datetime.utcnow()):
    """Converts a datetime object to unix epoch time in milliseconds"""
    unix_epoch_time_ms = int(dt.timestamp() * 1000)
    return unix_epoch_time_ms

def flatten_dict(d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)