"""
This type stub file was generated by pyright.
"""

def cleanNoneValue(d) -> dict:
    ...

def check_required_parameter(value, name): # -> None:
    ...

def check_required_parameters(params): # -> None:
    """validate multiple parameters
    params = [
        ['btcusdt', 'symbol'],
        [10, 'price']
    ]

    """
    ...

def check_enum_parameter(value, enum_class): # -> None:
    ...

def check_type_parameter(value, name, data_type): # -> None:
    ...

def get_timestamp(): # -> int:
    ...

def encoded_string(query, special=...): # -> str:
    ...

def convert_list_to_json_array(symbols): # -> str:
    ...

def config_logging(logging, logging_devel, log_file=...): # -> None:
    ...
