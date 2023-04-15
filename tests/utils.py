
from pathlib import Path
from src.utility import get_file_path

def write_to_tests_out_file(content, filename):
    cwd = Path.cwd()
    dir_path = cwd.joinpath('tests/out')
    filename = dir_path.joinpath(filename)
    with open(filename, 'w') as f:
        f.write(content)

def init_logging():
    import logging
    logging.basicConfig(filename=get_file_path('logs/testing.log'), encoding='utf-8', level=logging.DEBUG)
