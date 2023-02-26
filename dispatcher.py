from functools import wraps
from inspect import signature
from enum import Enum

def dispatcher(func):
    """This is a multi-arguments dispatcher based on a signature 
    introspection approach.
    This method can be used withing a class or a stand-alone function.
    
    Upon method registration - to be made on a non-executable parent - 
    multiple methods/functions can be recalled using the parenting
    function name. 

    The function includes a pairing mechanism (far to be perfect), that
    recall methods with the closest signature when a method/function is
    recalled with a non-exact signature. 
    If no matches are found, an exception is thrown. 
    """
    _registry = {}
    __arguments = {}
    
    def register(func):
        # Recover the parameters dictionary
        fnc_to_reg = []
        arguments = []
        sig = signature(func)

        for p in sig.parameters.values():
            # Parse the signature to build the entry point
            # For each parameter, do recognise:
            # - the type of a value
            # - the value itself
            # - the name 
            # - the type of paraneter (whether positional or keyword)
            
            # Manage the possibility the decorator to be used in class
            if p.name == 'self':
                continue

            # Capturing the value of my parameter; 
            # Taking into account an Enum can passed
            # Ovveriding the kind of value for later chechcks
            if isinstance(p.default, Enum):
                # Here the Enum was having a default value attached
                value = p.default#.value
                kind = 5 
            elif 'enum' in str(p.annotation):
                # Here it's an Enum without a default value 
                value = 'empty'
                kind = 5
            elif p.annotation.__name__ != '_empty' and p.kind.value == 1:
                value = 'empty' if '_empty' in str(p.default) else p.default
                kind = 4

            # elif isinstance(p.default, type):
            #     # original
            #     value = 'empty'
            #     kind = 4
            else:
                value = 'empty' if '_empty' in str(p.default) else p.default
                kind = p.kind.value 

            if p.annotation.__name__ == '_empty':
                method_sig = 'any' if type(p.default).__name__ == 'type' else type(p.default).__name__
            else: 
                method_sig = p.annotation.__name__
                # method_sig = p.name

            arguments.append((p.name, kind, method_sig, value))

            # method_sig = p.name if value != 'empty' else method_sig
            fnc_to_reg.append(method_sig)

        fnc_to_reg = tuple(fnc_to_reg)

        if fnc_to_reg not in _registry.keys():
            # If the signature has never been used before
            _registry.update({fnc_to_reg: func})
            __arguments.update({fnc_to_reg: arguments})

    def __get_signature(*args, **kwargs):
        '''Private function to build the signatures from the callee.'''
        def sig_pack(arg, value = None):
            if value:
                # Keyword arg
                n = arg
                # Manage the Enum type
                k = 5 if isinstance(value, Enum) or 'enum' in str(type(value)) else 4
                t = type(value).__name__
                v = value
            else:
                # positional arg
                n = (t if (t := arg.__class__.__name__) != 'type' else arg.__name__) #'any'
                # Manage the Enum type if any or factoring the positional tyepe.
                # A 'positional only' or 'positional/keyword' is a positional arg, hence 1.
                k = 5 if isinstance(arg, Enum) or 'enum' in str(type(arg)) else 1
                t =  type(arg).__name__ #(t if (t := arg.__class__.__name__) != 'type' else arg.__name__)
                v = arg 

            return tuple((n, k, t, v))

        signature_ = []

        # Positional arg
        try:
            for arg in args:
                # Skip the self parameter if any
                if hasattr(arg, func.__name__):
                    continue

                signature_.append(sig_pack(arg))
        except:
            pass

        # Keywords args
        try:
            for name, val in kwargs.items():
                signature_.append(sig_pack(name, val))
        except:
            pass

        return signature_

    def __match_signature(arguments, sig_check, match_type, include_generic):
        '''Private function to find out matching signatures.
            The check is purely based on numerical numbers and looking for
            generic parameters if requested.

            An in-depth check is done with a separate function.
        '''
        def sigExactMatch(k):
            return True if include_generic else k == sig_check
            
        matched = []

        match match_type:
            case 'exact' | '==':
                matched = [k for k in arguments.keys() if len(k) == len(sig_check) and sigExactMatch(k)]
            case 'greater' | '>' | 'gt':
                matched = [k for k in arguments.keys() if len(k) > len(sig_check) and sigExactMatch(k)]
            case 'lower' | '<' | 'lt':
                matched = [k for k in arguments.keys() if len(k) < len(sig_check) and sigExactMatch(k)]
            case 'greater equal' | '>=' | 'gte':
                matched = [k for k in arguments.keys() if len(k) >= len(sig_check) and sigExactMatch(k)]
            case 'lower equal' | '<=' | 'lte':
                matched = [k for k in arguments.keys() if len(k) <= len(sig_check) and sigExactMatch(k)]

        match include_generic:
            case 'Generics': 
                filtered = iter(matched)
                idx = 0

                while True:
                    try:
                        current = next(filtered)
                        if 'any' in current:
                            matched.pop(idx)
                    except StopIteration:
                        break
                    idx += 1

            case False | 'Only':
                filtered = iter(matched)
                idx = 0

                while True:
                    try:
                        current = next(filtered)
                        if include_generic == False:
                            if 'any' in current:
                                matched.pop(idx)
                        else:
                            if 'any' not in current:
                                matched.pop(idx)
                    except StopIteration:
                        break
                    idx += 1
            case _:
              pass

        return matched

    def __bind_signature(matches, *args, **kwargs):
        '''Private function to attempt binding the given arguments
        with a possible signature, then launch the dispatch. 
        
        Args:
            matches: contains the matched signatures
            args & kwargs: the arguments that will dispatched
        '''
        for idx, sig in enumerate(matches):
            try:
                sig_test = signature(_registry.get(matches[idx]))
                sig_test.bind(*args, **kwargs)

                try:
                    return _registry[tuple(sig)](*args, **kwargs)
                except KeyError:
                    pass
            except:
                continue

        return NotImplemented

    def dispatch(*args, **kwargs):
        if args and hasattr(args[0], func.__name__):
            # avoid parsing the self parameter when inside a class
            if len(args[1:]) == 0 and len(kwargs) == 0:
                return args[0]

            full_sig = __get_signature(*args[1:], **kwargs)
        else:
            if len(args) == 0 and len(kwargs) == 0:
                raise NotImplementedError("No suitable method exists.")

            full_sig = __get_signature(*args, **kwargs)

        try:
            # recall assuming a correct signature was given
            sig = tuple((i[0] for i in full_sig))
            return _registry[sig](*args, **kwargs)
        except KeyError: 
            #TODO: Sig_type and sig can be the same, avoid the call
            try:
                # Attempt to dispatch to the same method but by signature type
                sig = tuple((i[2] for i in full_sig))
                return _registry[sig](*args, **kwargs)
            except TypeError:
                raise NotImplementedError("No suitable method exists.")

            except KeyError:
                ret = NotImplemented
                
                # Case 1)
                # Recalling with the binding approach, any non-matching signature is
                # captured by a TypeError managed within the exception
                # matching_sigs = __match_signature(__arguments, full_sig, '==', False)
                matching_sigs = __match_signature(__arguments, sig, '==', False)
                if len(matching_sigs) > 0:
                    ret = __bind_signature(matching_sigs, *args, **kwargs)
                    if ret is not NotImplemented: return ret
                
                # Case 2)
                # Check for alternative method whose signature could be compatible
                matching_sigs = __match_signature(__arguments, sig, '>=', False)
                if len(matching_sigs) > 0: 
                    ret = __bind_signature(matching_sigs, *args, **kwargs)
                    if ret is not NotImplemented: return ret

                # Case 3)
                # Check for alternative method with default arguments
                matching_sigs = __match_signature(__arguments, sig, '>=', 'Generics')
                if len(matching_sigs) > 0: 
                    ret = __bind_signature(matching_sigs, *args, **kwargs)
                    if ret is not NotImplemented: return ret
                                    
                # Case 4)
                # Last attempt, trying to dispatch to a generic if it exists
                matching_sigs = __match_signature(__arguments, sig, '>=', 'Only')
                if len(matching_sigs) > 0: 
                    ret = __bind_signature(matching_sigs, *args, **kwargs)
                    if ret is not NotImplemented: return ret
                
            if ret is NotImplemented:
                raise NotImplementedError("No suitable method exists.")

    @wraps(func)
    def wrapper(*args, **kwargs):
        return dispatch(*args, **kwargs)

    wrapper.register = register
    wrapper.registry = _registry
    
    return wrapper
