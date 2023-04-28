
from pathlib import Path
from src.util import get_logger

class TestLogger:
    pass

test_logger = get_logger(TestLogger)

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

def get_test_out_absolute_path(filename):
    cwd = Path.cwd()
    dir_path = cwd.joinpath('tests/out')
    path = dir_path.joinpath(filename).absolute()
    return str(path)



    
