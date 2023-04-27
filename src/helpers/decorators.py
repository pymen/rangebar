def config(**kwargs):
    def decorator(func):
        for key, value in kwargs.items():
            setattr(func, key, value)
        func.is_config = True
        return func
    return decorator

def consumer_source(**kwargs):
    def decorator(cls):
        for key, value in kwargs.items():
            setattr(cls, key, value)
        cls.is_consumer_source = True
        return cls
    return decorator
  