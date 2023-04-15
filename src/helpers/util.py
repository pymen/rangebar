
from datetime import datetime

def get_unix_epoch_time_ms(dt: datetime = datetime.utcnow()):
    """Converts a datetime object to unix epoch time in milliseconds"""
    unix_epoch_time_ms = int(dt.timestamp() * 1000)
    return unix_epoch_time_ms