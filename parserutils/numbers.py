from math import isnan, isinf


def is_number(num, if_bool=False):
    """ :return: True if num is either an actual number, or an object that converts to one """

    if isinstance(num, bool):
        return if_bool
    elif isinstance(num, int):
        return True

    try:
        number = float(num)
        return not (isnan(number) or isinf(number))
    except (TypeError, ValueError):
        return False
