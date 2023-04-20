
from pathlib import Path
from src.util import get_logger

logging = get_logger('tests')

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



    
