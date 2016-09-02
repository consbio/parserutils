from math import isnan, isinf


def is_number(num, if_bool=False):
    """ :return: True if 's' is an actual number, or an object that represents one """

    if isinstance(num, bool):
        return if_bool
    elif isinstance(num, int):
        return True
    try:
        number = float(num)
        return not (isnan(number) or isinf(number))
    except (TypeError, ValueError):
        return False
