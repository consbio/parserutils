from six import iteritems, string_types
from parserutils.strings import EMPTY_STR


# DICT FUNCTIONS #


def setdefaults(d, defaults):
    """
    If defaults is a str, updates a dict with None at an optionally dot-notated key:
        'a.b' --> {'a': {'b': None}}
    If defaults is a list, updates a dict with None at each optionally dot-notated key:
        ['a.b', 'a.c'] --> {'a': {'b': None, 'c': None}}
    If defaults is a dict, applies keys as fields and values as defaults:
        {'a.b': 'bbb', 'a.c': 'ccc'} --> {'a': {'b': 'bbb', 'c': 'ccc'}}
        {'a.b.c': 'ccc', 'a.c.d.e': 'eee'} --> {'a': {'b': {'c': 'ccc'}, 'c': {'d': {'e': 'eee'}}}}
    """

    def to_key_val_pairs(defs):
        """ Helper to split strings, lists and dicts into (key, value) tuples for accumulation """

        if isinstance(defs, string_types):
            return [defs.split('.', 1) if '.' in defs else (defs, None)]
        elif isinstance(defs, dict):
            return to_key_val_pairs([defs])
        else:
            pairs = []
            pairs.extend(p for s in defs if isinstance(s, string_types) for p in to_key_val_pairs(s))
            pairs.extend(p for l in defs if isinstance(l, list) for p in to_key_val_pairs(l))
            pairs.extend(p for d in defs if isinstance(d, dict) for p in iteritems(d))
            return pairs

    if not isinstance(d, dict) or defaults is None:
        return d
    elif isinstance(defaults, (string_types, dict)):
        return setdefaults(d, [defaults])  # Wrap in list for consistent behavior
    else:
        use_none = all(isinstance(s, string_types) for s in defaults)

        # Accumulate (key, value) tuples to be applied to d
        accumulated = {}
        for key, val in to_key_val_pairs(defaults):
            accumulated.setdefault(key, [])
            if val is not None:
                accumulated[key].append(val)

        # Update d with accumulated (key, value) pairs, handling nested dot-notated keys
        for key, val in iteritems(accumulated):
            v = val[0] if val else None

            if use_none:
                default = setdefaults({}, val) if v else None
                if default and isinstance(d.get(key), dict):
                    d[key].update(default)
                else:
                    d.setdefault(key, default)
            elif '.' not in key:
                d.setdefault(key, v if isinstance(v, string_types) else setdefaults({}, val) or v)
            else:
                k, s = key.split('.', 1)
                d.setdefault(k, {})
                setdefaults(d[k], [{s: v}])

        return d


# LIST, SET, ETC FUNCTIONS #


def filter_empty(values, default=None):
    """
    Eliminates None or empty items from lists, tuples or sets passed in.
    If values is None or empty after filtering, the default is returned.
    """

    def is_empty(val):
        return hasattr(val, '__len__') and len(val) == 0

    if values is None:
        return default
    elif is_empty(values):
        return default
    elif isinstance(values, (list, tuple, set)):
        values = type(values)(v for v in values if not (v is None or is_empty(v)))
        return default if is_empty(values) else values

    return values


def reduce_value(value, default=EMPTY_STR):
    """
    :return: the item from lists, tuples or sets with one item, the value itself if not empty, otherwise the default
    """

    if hasattr(value, '__len__'):
        vlen = len(value)

        if vlen == 0:
            return default
        elif vlen == 1:
            if isinstance(value, set):
                return value.pop()
            elif isinstance(value, (list, tuple)):
                return value[0]

    return default if value is None else value


def wrap_value(value):
    """
    :return: the value wrapped in a list unless it is already iterable (and not a dict)
    """

    if value is None:
        return []
    elif hasattr(value, '__len__') and len(value) == 0:
        return []
    elif isinstance(value, (string_types, dict)):
        return [value]
    elif not hasattr(value, '__iter__'):
        return [value]

    return value
