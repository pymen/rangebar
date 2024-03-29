"""
This type stub file was generated by pyright.
"""

class Error(Exception):
    ...


class ClientError(Error):
    def __init__(self, status_code, error_code, error_message, header) -> None:
        ...
    


class ServerError(Error):
    def __init__(self, status_code, message) -> None:
        ...
    


class ParameterRequiredError(Error):
    def __init__(self, params) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    


class ParameterValueError(Error):
    def __init__(self, params) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    


class ParameterTypeError(Error):
    def __init__(self, params) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    


class ParameterArgumentError(Error):
    def __init__(self, error_message) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    


