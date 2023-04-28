import json
import logging
import sys
from pathlib import Path
from typing import Dict, Self
import os
import glob
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

def get_root_data_dir() -> Path:
    """
    Get path where trader is running in.
    """
    cwd = Path.cwd()
    return cwd.joinpath('resources')

sys.path.append(str(Path.cwd()))


def get_file_path(filename: str) -> Path:
    """
    Get abs path.
    """
    file_path = get_root_data_dir().joinpath(filename).resolve()
    return file_path



def load_json(filename: str) -> dict[str, str | int]:
    """
    Load data from json file path.
    """
    filepath = get_file_path(filename)

    if filepath.exists():
        with open(filepath, mode="r", encoding="UTF-8") as f:
            data = json.load(f)
        return data
    else:
        save_json(filename, {})
        return {}


def save_json(filename: str, data: dict[str, str | int]) -> None:
    """
    Save data into json file path.
    """
    filepath = get_file_path(filename)
    with open(filepath, mode="w+", encoding="UTF-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

file_handlers: Dict[str, logging.FileHandler] = {}
logging.basicConfig(level=logging.DEBUG, force=True)
settings = get_settings('app')

def clear_logs():
    directory = str(get_file_path('logs').absolute())
    log_files = glob.glob(directory + '/*.log')
    for log_file in log_files:
        os.remove(log_file)

def clear_symbol_windows():
    directory = str(get_file_path('symbol_windows').absolute())
    csv_files = glob.glob(directory + f'/*.{settings["storage_ext"]}')
    for csv_file in csv_files:
        os.remove(csv_file)        



def _get_file_logger_handler(filename: str) -> logging.FileHandler:
    handler = file_handlers.get(filename, None)
    if handler is None:
        handler = logging.FileHandler(filename)
        file_handlers[filename] = handler  # Am i need a lock?
    return handler

def to_snake_case(text: str) -> str:
    import re
    words = re.findall('[a-z]+|[A-Z][a-z]*', text)
    return '_'.join(word.lower() for word in words)

def get_logger(cls: object) -> logging.Logger:
    """
    return a logger that writes records into a file.
    """
    name = cls.__class__.__name__
    filename = str(get_file_path(f'logs/{to_snake_case(name)}.log').absolute())
    log_formatter = logging.Formatter('[%(asctime)s][%(threadName)s](%(levelname)s) %(name)s: %(message)s')
    logger = logging.getLogger(name)
    handler = _get_file_logger_handler(filename)  # get singleton handler.
    handler.setFormatter(log_formatter)
    logger.addHandler(handler)  # each handler will be added only once.
    return logger