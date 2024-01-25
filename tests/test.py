from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dispatcher import dispatcher


@dispatcher
def foo():
    """Not implemented"""
    raise NotImplementedError("Method not implementated on purpose.")


@foo.register
def _(dimension: str, expression: str, operator: str, append: bool):
    # argtype = [f"{__arg}: {type(locals()[__arg]).__name__} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    argtype = [f"{__arg} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    print(f"Inbound args: {argtype}")
    print('')
    return argtype


@foo.register
def _(arg: int):
    # argtype = [f"{__arg}: {type(locals()[__arg]).__name__} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    argtype = [f"{__arg} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    print(f"Inbound args: {argtype}")
    print('')
    return argtype


@foo.register
def _(arg: list, b: bool = True):
    # argtype = [f"{__arg}: {type(locals()[__arg]).__name__} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    argtype = [f"{__arg} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    print(f"Inbound args: {argtype}")
    print('')
    return argtype


@foo.register
def _(arg: list):
    """This will return a list implementation."""
    # argtype = [f"{__arg}: {type(locals()[__arg]).__name__} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    argtype = [f"{__arg} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    print(f"Inbound args: {argtype}")
    print('')
    return argtype

    # print(inspect.stack()[0][3])
    # print(inspect.stack()[0][0].f_code.co_name)
    # print(inspect.currentframe().f_code.co_name)
    # print(sys._getframe().f_code.co_name)
    # name = sys._getframe().f_code.co_name
    # inspect.signature(name).parameters
    # print(inspect.getmembers(inspect.stack()[0].function))
    # print(inspect.currentframe().__getattribute__())


@foo.register
def _(arg: str):
    signature = locals()
    print(f"Inbound arguments: {signature}")
    # argtype = [f"{__arg}: {type(locals()[__arg]).__name__} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    argtype = [f"{__arg} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    print(f"Inbound args: {argtype}")
    print('')
    return argtype


@foo.register
def _(country: str = ''):
    x = sys._getframe().f_code.co_name
    # argtype = [f"{__arg}: {type(locals()[__arg]).__name__} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    argtype = [f"{__arg} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    print(f"Inbound args: {argtype}")
    print('')
    return argtype


@foo.register
def _(country, operator, append):
    # argtype = [f"{__arg}: {type(locals()[__arg]).__name__} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    argtype = [f"{__arg} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    print(f"Inbound args: {argtype}")
    print('')
    return argtype


@foo.register
def _(country: str, operator: str = 'and', append: bool = False):
    # argtype = [f"{__arg}: {type(locals()[__arg]).__name__} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    argtype = [f"{__arg} = {locals()[__arg]}" for _ in dir() if (__arg:=_)]
    print(f"Inbound args: {argtype}")
    print('')
    return argtype


if __name__ == '__main__':
    ret = foo([1, 2, 3])
    # Expected to call arg:list
    # If the method does not exist, it calls arg:str
    # Dispatch to a generic alternative
    assert str(ret) == "['arg = [1, 2, 3]']", \
        f"The recalled method was not the " \
        f"type-defined function with 'arg:list' argument(s). " \
        f"Method signature recalled: {ret}"

    # Expected to call arg:int
    ret = foo(1)
    assert str(ret) == "['arg = 1']", \
        f"The recalled method was not the " \
        f"type-defined function with 'arg:int' argument(s). "\
        f"Method signature recalled: {ret}"

    # Expected to call (country, operator, append)
    ret = foo('a', 'b', 'c')
    assert str(ret) == "['append = c', 'country = a', 'operator = b']", \
        f"The recalled method was not the " \
        f"generic function with 'country, operator, append' argument(s). "\
        f"Method signature recalled: {ret}"

    ret = foo(1, 2, 3)
    assert str(ret) == "['append = 3', 'country = 1', 'operator = 2']", \
        f"The recalled method was not the " \
        f"generic function with 'country, operator, append' argument(s). " \
        f"Method signature recalled: {ret}"

    ret = foo('test')
    # Expected to call (arg: str) if not commented
    #### else (country: str, operator: str = 'and', append: bool = False)
    #### The two methods cannot exist together
    assert str(ret) == "['arg = test']", \
        f"The recalled method was not the \
        type-defined function with 'arg:str' argument(s). \
        Method signature recalled: {ret}"

    ret = foo(country='test')
    # Expected to call (arg: str) if not commented
    # else (country: str = '')
    # The two methods cannot exist together
    assert ret == "['country = test'}", \
        f"The recalled method was not the \
        type-defined function with 'country:str' argument(s). \
        Method signature recalled: {ret}"

    # Expected to call (country: str, operator: str, append: bool)
    # receiving country = test, operator = 'plus' and defaulting the append to False
    ret = foo('test', 'plus')
    assert ret != "{'country': 'test'}", \
        f"The recalled method was not the \
        type-defined function with 'country:str' argument(s). \
        Method signature recalled: {ret}"
