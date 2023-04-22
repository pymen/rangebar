def config(**kwargs):
    def decorator(func):
        for key, value in kwargs.items():
            setattr(func, key, value)
        func.is_config = True
        return func
    return decorator

def consumer_source(stream_name: str = None, event_source: object = None):
    def decorator(cls):
        cls.source_name = stream_name
        cls.event_source = event_source
        return cls
    return decorator