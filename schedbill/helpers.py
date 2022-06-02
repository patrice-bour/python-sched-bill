def is_float(num):
    """"""

    try:
        float(num)
    except ValueError:
        return False
    return True
