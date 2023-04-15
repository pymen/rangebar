"""
General utility functions.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Callable, Dict, Tuple



def get_root_data_dir() -> Path:
    """
    Get path where trader is running in.
    """
    cwd = Path.cwd()
    return cwd.joinpath('data')

sys.path.append(str(Path.cwd()))


def get_file_path(filename: str) -> Path:
    """
    Get abs path.
    """
    file_path = get_root_data_dir().joinpath(filename).resolve()
    return file_path



def load_json(filename: str) -> dict:
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


def save_json(filename: str, data: dict) -> None:
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

        

def virtual(func: Callable) -> Callable:
    """
    mark a function as "virtual", which means that this function can be override.
    any base class should use this or @abstractmethod to decorate all functions
    that can be (re)implemented by subclasses.
    """
    return func


file_handlers: Dict[str, logging.FileHandler] = {}


def _get_file_logger_handler(filename: str) -> logging.FileHandler:
    handler = file_handlers.get(filename, None)
    if handler is None:
        handler = logging.FileHandler(filename)
        file_handlers[filename] = handler  # Am i need a lock?
    return handler



def get_logger(filename: str) -> logging.Logger:
    """
    return a logger that writes records into a file.
    """
    log_formatter = logging.Formatter('[%(asctime)s] %(message)s')
    logger = logging.getLogger(filename)
    handler = _get_file_logger_handler(filename)  # get singleton handler.
    handler.setFormatter(log_formatter)
    logger.addHandler(handler)  # each handler will be added only once.
    return logger