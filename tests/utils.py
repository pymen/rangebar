
from pathlib import Path
from src.utility import get_file_path

def write_to_tests_out_file(content, filename):
    cwd = Path.cwd()
    dir_path = cwd.joinpath('tests/out')
    filename = dir_path.joinpath(filename)
    with open(filename, 'w') as f:
        f.write(content)

def read_from_tests_out_json_to_dict(filename):
    import json
    cwd = Path.cwd()
    dir_path = cwd.joinpath('tests/out')
    filename = dir_path.joinpath(filename)
    with open(filename) as f:
        data = json.load(f)
    return data


def init_logging():
    import logging
    logging.basicConfig(filename=get_file_path('logs/testing.log'), encoding='utf-8', level=logging.DEBUG)
