from math import isnan, isinf


def is_number(s):
    try:
        number = float(s)
        return not (isnan(number) or isinf(number))
    except (TypeError, ValueError):
        return False
