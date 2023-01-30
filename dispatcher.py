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
    # __default_args = {}
    
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
                value = p.default
                kind = p.kind.value 

            if p.annotation.__name__ == '_empty':
                method_sig = 'any' if type(p.default).__name__ == 'type' else type(p.default).__name__
            else: 
                method_sig = p.annotation.__name__

            arguments.append((p.name, kind, method_sig, value))

            method_sig = p.name if value != 'empty' else method_sig
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
                # It doesn't matter whether an arg is positional only or positional/keyword. 
                # At this state to me those are all positionals, hence 1.
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

    def __match_signature(arguments, sig_len_check, include_generic):
        '''Private function to find out all the possible matching signatures.
            The check is purely based on numerical numbers and looking for
            generic parameters if requested.
            
            An in-depth check is done with a separate function.'''
        def flat_list(list_):
            # flatten the list
            flat_list = []
            for i in list_:
                flat_list += i
            return flat_list
        
        if include_generic:
            matched = []
            for k in arguments.keys():
                # if len(k) == len(sig_len_check):
                if eval(str(len(k))+sig_len_check):
                    flatten = flat_list(arguments.get(k))
                    if 'any' not in flatten:
                        matched.append(k)
            return matched
        else:
            return [k for k in arguments.keys() if eval(str(len(k))+sig_len_check)]
            # return [k for k in arguments.keys() if len(k) == len(sig_len_check)]
            
    def __get_argument(mfs_to_eval, current_arg):
        '''Private function to determine the correspondance between 
        a single calling argument and its corresponding recepient.
        
        Args:
            mfs_to_eval: is the single argument in the evaluated signature
            current_arg: is the single argument being assessed
        '''
        proceed = False
        
        # Determine the type
        match mfs_to_eval[1]:
            case 1:
                # It's a positional only argument. Only type can match
                if type(mfs_to_eval[3]).__name__ == current_arg[2]:
                # if isinstance(mfs_to_eval[3], eval(current_arg[2])):
                    proceed = True
            case 4:
                # It's a keyword argument. Both type and name should match
                if mfs_to_eval[1] == current_arg[1] and mfs_to_eval[2] == current_arg[2]:
                    proceed = True
            case 5:
                # It's an enum argument. Only type can match
                if mfs_to_eval[2] == current_arg[2]:
                    proceed = True
            case _:
                # Added as a precaution. It should not happen
                raise TypeError("This type is not supported yet.") from None
        
        if not proceed:
            return None

        else:
            if mfs_to_eval[3] != 'empty':
                # The argument was passed
                return {current_arg[0]: mfs_to_eval[3]}
            elif current_arg[3] != 'empty':
                # The default value is used if any
                return {current_arg[0]: current_arg[3]}
            
    def __is_sig_partial(sig_to_check, against):
        # Need to check for signature length as well as if there is 
        # any optional that will allow me to progress later
        fitting_args = 0
        default_args = 0
        other_args = 0

        for index, item in enumerate(sig_to_check):
            # fitting_args += 1 if item[2] == against[index][2] and against[index][3] == 'empty' else 0
            # default_args += 1 if item[2] == against[index][2] and against[index][3] != 'empty' else 0
            
            if item[2] == against[index][2] and against[index][3] == 'empty':
                fitting_args += 1
                continue
            
            # At this stage can be an optional argument
            if against[index][3] != 'empty':
                default_args += 1 
        
        for item in against[index + 1:]:
            other_args += 1 if against[index + 1][3] != 'empty' else 0

        return (fitting_args + default_args + other_args) == len(against)
    
    def __find_argument(sig_to_check, arg):
            # I can have only one matching combination
            try:
                # return [index for index, i in enumerate(sig_to_check) if arg[0] == i[0] and arg[2] == i[2]][0]
                return [index for index, i in enumerate(sig_to_check) if arg[2] == i[2]][0]
            except:
                return None

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
        except KeyError: #TODO: Sig_type and sig can be the same, avoid the call
            try:
                # Attempt to dispatch to the same method but by signature type
                sig = tuple((i[2] for i in full_sig))
                return _registry[sig](*args, **kwargs)
            except TypeError:
                raise NotImplementedError("No suitable method exists.")

            except KeyError:
                # Case 1: argument length the same, signature different
                # Case 2: argument length different, have default values
                # Case 3: argument length the same, generic signature

                # Case 1)
                # Recalling assuming the arguments number is the same and its type matches
                # No positional arguments 
                matching_sigs = __match_signature(__arguments, '=='+str(len(full_sig)), False)

                if len(matching_sigs) > 0:
                    for i in matching_sigs:
                        sig_repl = []

                        for index, this_sig in enumerate(__arguments.__getitem__(i)):
                            # Only if signature name and type matches
                            # This is to prevent calls when keyword arguments only exists but the signature is different 
                            if this_sig[2] == full_sig[index][2] and type(full_sig[index][3]) == type(this_sig[2]):
                                # There is a matching by type
                                sig_repl.append(i[index])

                        if len(sig_repl) > 0:
                            try:
                                return _registry[tuple(sig_repl)](*args, **kwargs)
                            except KeyError:
                                pass

                        del(this_sig)
                        del(sig_repl)

                # Case 2)
                # Check for alternative method whose signature could be compatible
                matching_sigs = __match_signature(__arguments, '>='+str(len(full_sig)), False)

                if len(matching_sigs) > 0:
                    for match in matching_sigs:
                        # Process the suggested match against the retrieved calling signature
                        metfun_sig_args = __arguments.get(match)

                        if __is_sig_partial(full_sig, metfun_sig_args):
                            kwargs.clear()
                            metfun_sig_args = iter(metfun_sig_args)

                            while True:
                                try:
                                    msa = next(metfun_sig_args)
                                except StopIteration:
                                    break
                                else:
                                    arg_idx = __find_argument(full_sig, msa)

                                    if arg_idx is None:
                                        kwargs.update({msa[0]: msa[3]})
                                    else:
                                        # if no arg matches, then grab the default value. There should be one
                                        kwargs.update(__get_argument(full_sig[arg_idx], msa))

                            if len(kwargs) == len(match):
                                try:
                                    if args and hasattr(args[0], func.__name__): 
                                        return _registry[match](args[0], **kwargs)
                                    else:
                                        return _registry[match](**kwargs)
                                except KeyError:
                                    pass

                # Case 3)
                # Last attempt, trying to dispatch to a generic if it exists
                # Receiving call might have been not designed for the input
                matching_sigs = __match_signature(__arguments, '>='+str(len(full_sig)), True)

                if len(matching_sigs) > 0:
                    sig = tuple((i[3] for i in full_sig))
                    # I should have only one function left here
                    for match in matching_sigs:
                        if len(full_sig) == len(match):
                            try:
                                if args and hasattr(args[0], func.__name__): 
                                    return _registry[match](args[0], *sig)
                                else:
                                    return _registry[match](*sig)
                            except KeyError:
                                pass

            raise NotImplementedError("No suitable method exists.")

    @wraps(func)
    def wrapper(*args, **kwargs):
        return dispatch(*args, **kwargs)

    wrapper.register = register
    wrapper.registry = _registry
    
    return wrapper