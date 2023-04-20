"""
Global setting of Binance Grid Trader.
"""
from logging import DEBUG
from typing import Dict, Any

from .util import load_json

SETTINGS: Dict[str, Any] = {
    "font.family": "Arial",
    "font.size": 12,
    "log.active": True,
    "log.level": DEBUG,
    "log.console": True,
    "log.file": True
}

# Load global setting from json file.
SETTING_FILENAME: str = "settings.json"
SETTINGS.update(load_json(SETTING_FILENAME))


def get_settings(prefix: str = "") -> Dict[str, Any]:
    prefix_length = len(prefix)
    return {k[prefix_length:].split('.')[1]: v for k, v in SETTINGS.items() if k.startswith(prefix)}
