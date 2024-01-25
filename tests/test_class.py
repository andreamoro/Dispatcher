from __future__ import annotations
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dispatcher import dispatcher


class test():
    """This is a test class"""
    def __init__(self) -> None:
        self.array = [1, 2, 3]

    @dispatcher
    def foo():
        raise NotImplementedError("This method has not been implementated on purpose.")

    @foo.register
    def _(self, dimension:float):
        print('')
        print("dimension: float")
        print(f"dimension: {dimension}")

    @foo.register
    def _(self, arg:int):
        print('')
        print("arg:int")
        print(f"arg:{arg}")

        for i in self.array:
            print(i)


if __name__ == '__main__':
    t = test()
    # Expected to call arg:list
    # If the method does not exist, it calls arg:str
    # Dispatch to a generic alternative
    t.foo(1.0)
