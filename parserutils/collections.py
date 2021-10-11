from _collections import defaultdict

from .strings import DEFAULT_ENCODING, STRING_TYPES


_BASE_VALUE_TYPES = (dict,) + STRING_TYPES


# DICT FUNCTIONS #


def accumulate_items(items, reduce_each=False):
    """ :return: item pairs as key: val, with vals under duplicate keys accumulated under each """

    if not items:
        return {}

    accumulated = defaultdict(list)
    for key, val in items:
        accumulated[key].append(val)

    if not reduce_each:
        return accumulated
    else:
        return {k: reduce_value(v, v) for k, v in accumulated.items()}


def setdefaults(d, defaults):
    """
    If defaults is a str, updates a dict with None at an optionally dot-notated current:
        'a.b' --> {'a': {'b': None}}
    If defaults is a list, updates a dict with None at each optionally dot-notated current:
        ['a.b', 'a.c'] --> {'a': {'b': None, 'c': None}}
    If defaults is a dict, applies keys as fields and values as defaults:
        {'a.b': 'bbb', 'a.c': 'ccc'} --> {'a': {'b': 'bbb', 'c': 'ccc'}}
        {'a.b.c': 'ccc', 'a.c.d.e': 'eee'} --> {'a': {'b': {'c': 'ccc'}, 'c': {'d': {'e': 'eee'}}}}
    """

    if not isinstance(d, dict) or defaults is None:
        return d
    elif isinstance(defaults, _BASE_VALUE_TYPES):
        defaults = [defaults]

    use_none = not any(isinstance(s, dict) for s in defaults)

    # Accumulate (current, remaining) pairs to be applied to d

    accumulated = {}
    for current, remaining in _to_key_val_pairs(defaults):
        accumulated.setdefault(current, [])
        if remaining is not None:
            accumulated[current].append(remaining)

    # Update d with accumulated pairs, handling further nested dot-notated keys

    for current, remaining in accumulated.items():
        if use_none:

            # Apply None value for what remains of the dot notated key
            defaults = setdefaults(d.get(current, {}), remaining) if remaining else None
            if defaults and isinstance(d.get(current), dict):
                d[current].update(defaults)
            else:
                d.setdefault(current, defaults)

        else:
            next_up = remaining[0] if remaining else None

            if '.' in current:
                # Split on the dot and process next segment
                k, s = current.split('.', 1)
                d.setdefault(k, {})
                setdefaults(d[k], [{s: next_up}])
            elif isinstance(next_up, STRING_TYPES):
                # Set a string value directly
                d.setdefault(current, next_up)
            else:
                # Process a dict value or just set to the value in next_up
                d.setdefault(current, setdefaults({}, remaining) or next_up)

    return d


def _to_key_val_pairs(defs):
    """ Helper to split strings, lists and dicts into (current, value) tuples for accumulation """

    if isinstance(defs, STRING_TYPES):
        # Convert 'a' to [('a', None)], or 'a.b.c' to [('a', 'b.c')]
        return [defs.split('.', 1) if '.' in defs else (defs, None)]
    else:
        pairs = []

        # Convert collections of strings or lists as above; break dicts into component items
        pairs.extend(p for s in defs if isinstance(s, STRING_TYPES) for p in _to_key_val_pairs(s))
        pairs.extend(p for l in defs if isinstance(l, (list, tuple)) for p in _to_key_val_pairs(l))
        pairs.extend(p for d in defs if isinstance(d, dict) for p in d.items())

        return pairs


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
    elif hasattr(values, '__iter__') and not isinstance(values, _BASE_VALUE_TYPES):
        filtered = type(values) if isinstance(values, (set, tuple)) else list
        values = filtered(
            v for v in values if not (v is None or (hasattr(v, '__len__') and len(v) == 0))
        )
        return default if len(values) == 0 else values

    return values


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
    elif isinstance(items, _BASE_VALUE_TYPES):
        return items

    flattened = []
    for item in items:
        if item and hasattr(item, '__iter__') and not isinstance(item, _BASE_VALUE_TYPES):
            flattened.extend(flatten_items(item, True) if recurse else item)
        else:
            flattened.append(item)

    return type(items)(flattened) if isinstance(items, (set, tuple)) else flattened


def remove_duplicates(items, in_reverse=False, is_unhashable=False):
    """
    With maximum performance, iterate over items and return unique ordered values.
    :param items: an iterable of values: lists, tuples, strings, or generator
    :param in_reverse: if True, iterate backwards to remove initial duplicates (less performant)
    :param is_unhashable: if False, use a set to track duplicates; otherwise a list (less performant)
    :return: a unique ordered list, tuple or string depending on the type of items
    """

    if not items:
        return items
    elif isinstance(items, (dict, set)):
        return items  # Already reduced by definition
    elif not hasattr(items, '__iter__') and not hasattr(items, '__getitem__'):
        return items  # Only bytes, str, list, tuple, generator or custom collections beyond this

    _items = items
    if in_reverse:
        subscriptable = hasattr(items, '__getitem__')
        _items = items[::-1] if subscriptable else reversed([i for i in items])

    is_unhashable &= not isinstance(items, STRING_TYPES)
    buffer = [] if is_unhashable else set()
    append = buffer.append if is_unhashable else buffer.add

    if not isinstance(items, (bytes, str, tuple)):
        # The fastest case: lists are 33% faster than other cases, generators 25%
        unique = [i for i in _items if i not in buffer and not append(i)]
    elif isinstance(items, tuple):
        unique = tuple(i for i in _items if i not in buffer and not append(i))
    elif isinstance(items, str):
        unique = ''.join(i for i in _items if i not in buffer and not append(i))
    else:
        # For byte arrays, convert integers back to bytes during iteration
        unique = b''.join(bytes([i]) for i in _items if i not in buffer and not append(i))

    return unique if not in_reverse else unique[::-1]  # Restore original order


def rfind(values, value):
    """ :return: the highest index in values where value is found, or -1 """

    if isinstance(values, STRING_TYPES):
        try:
            return values.rfind(value)
        except TypeError:
            # Search for str values in byte array
            return values.rfind(type(values)(value, DEFAULT_ENCODING))
    else:
        try:
            return len(values) - 1 - values[::-1].index(value)
        except (TypeError, ValueError):
            return -1


def rindex(values, value):
    """ :return: the highest index in values where value is found, else raise ValueError """

    if isinstance(values, STRING_TYPES):
        try:
            return values.rindex(value)
        except TypeError:
            # Search for str values in byte array
            return values.rindex(type(values)(value, DEFAULT_ENCODING))
    else:
        return len(values) - 1 - values[::-1].index(value)


def reduce_value(value, default=''):
    """
    :return: a single value from lists, tuples or sets with one item;
    otherwise, the value itself if not empty or the default if it is.
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


def wrap_value(value, include_empty=False):
    """
    :return: the value wrapped in a list unless it is already iterable (and not a dict);
    if so, empty values will be filtered out by default, and an empty list is returned.
    """

    if value is None:
        return [None] if include_empty else []
    elif hasattr(value, '__len__') and len(value) == 0:
        return [value] if include_empty else []
    elif isinstance(value, _BASE_VALUE_TYPES):
        return [value]
    elif not hasattr(value, '__iter__'):
        return [value]

    return value if include_empty else filter_empty(value, [])
