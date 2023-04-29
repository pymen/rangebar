from abc import ABC, abstractmethod

class Singleton(ABC):
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    @abstractmethod
    def do_something(self):
        pass

class ChildClass(Singleton):
    
    # def __new__(cls):
    #     return super().__new__(cls)

    def do_something(self):
        print(f'hello world')

def test_singleton_inheritance():
    # Create two instances of ChildClass
    c1 = ChildClass() # type: ignore
    c2 = ChildClass() # type: ignore

    # Check if they are the same object
    same = c1 is c2
    print(f'same: {same}')
