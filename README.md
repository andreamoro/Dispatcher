# Multi-Arguments Dispatcher

[![License: GPL 3.0](https://www.gnu.org/graphics/gplv3-127x51.png)](https://www.gnu.org/licenses/gpl-3.0.txt)
    
This is a multi-arguments dispatcher based on a signature introspection approach written for a personal project and tested on both a class as well as on a set of stand-alone unit-tests.

The method was developed to provide a pairing mechanism support (far to be perfect) when a method/function is recalled and non-exact signature is found. If no matches are found, an exception is thrown.

## Usage
As soon as the method is imported, a non-executable function can be declared to create the dispatcher.

```python
@dispatcher
def foo():
    raise NotImplementedError("This method has not been implementated on purpose.")
```

This will form the main entry point (or method name) for which you want to create variants to be registered. At that point methods can be registered against the entry point as per the example below.

```python
@foo.register
def _(arg:int):
    print('')
    print("arg:int")
    print(f"arg:{arg}")

@foo.register
def _(country: str, operator: str = 'and', append: bool = False):
    print('')
    print("country: str, operator: str = 'and', append: bool = False")
    print(f"country: {country}, operator: {operator}, append: {append}")
```

When the method will be executed, it will attempt to resolve the version with an exact signature match first. If nothing is found, then the method will attempt to dispatch to the version with the closest signature up to throw a `NotImplementedError` if nothing is found.

This method does not behave as a variadic function, so methods have to expose the signature ones would expect to call. In contrast, an effort was put to support the default arguments.
