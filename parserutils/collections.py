from _collections import defaultdict

from six import iteritems, string_types

from parserutils.strings import EMPTY_STR, _STRING_TYPES


# DICT FUNCTIONS #


def accumulate(items, reduce_each=False):
    """ :return: item pairs as key: val, with vals under duplicate keys accumulated under each """

    if not items:
        return {}

    accumulated = defaultdict(list)
    for key, val in items:
        accumulated[key].append(val)

    if not reduce_each:
        return accumulated
    else:
        return {k: reduce_value(v, v) for k, v in iteritems(accumulated)}


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

    if values is None:
        return default
    elif hasattr(values, '__len__') and len(values) == 0:
        return default
    elif isinstance(values, _filter_types):
        values = type(values)(
            v for v in values
            if not (v is None or (hasattr(v, '__len__') and len(v) == 0))
        )
        return default if hasattr(values, '__len__') and len(values) == 0 else values

    return values

_filter_types = (list, tuple, set)


def flatten_items(items, recurse=False):
    """
    Expands inner lists (tuples, sets, Etc.) within items so that each extends its parent.
    If items is None or empty after filtering, the default is returned.
    If recurse is False, only the first level of items is flattened, otherwise all levels.
    """

    if not items:
        return items
    elif not hasattr(items, '__iter__'):
        return items
    elif isinstance(items, _flattened_types):
        return items

    flattened = []
    for item in items:
        if item and hasattr(item, '__iter__') and not isinstance(item, _flattened_types):
            flattened.extend(flatten_items(item, True) if recurse else item)
        else:
            flattened.append(item)

    return type(items)(flattened) if isinstance(items, _flatten_types) else flattened

_flatten_types = (tuple, set)
_flattened_types = (dict,) + _STRING_TYPES


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
            elif isinstance(value, _reduce_types):
                return value[0]

    return default if value is None else value

_reduce_types = (list, tuple)


def wrap_value(value, include_empty=False):
    """
    :return: the value wrapped in a list unless it is already iterable (and not a dict)
    If so, empty values will be filtered out by default, and an empty list is returned.
    """

    if value is None:
        return [None] if include_empty else []
    elif hasattr(value, '__len__') and len(value) == 0:
        return [value] if include_empty else []
    elif isinstance(value, _wrap_types):
        return [value]
    elif not hasattr(value, '__iter__'):
        return [value]

    return value if include_empty else filter_empty(value, [])

_wrap_types = (dict,) + _STRING_TYPES
