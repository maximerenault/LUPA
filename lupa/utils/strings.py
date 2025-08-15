def check_strint(strin: str) -> str:
    """Takes a string and removes characters that don't belong
    in a signed integer.

    >>> check_strint("")
    ""
    >>> check_strint("-")
    "-"
    >>> check_strint("-m080")
    "-80"

    Args:
        strin (str): string supposed to be a signed integer

    Returns:
        str: processed string
    """
    strout = ""
    leadingzeros = True
    nbleadingzeros = 0
    for i, c in enumerate(strin):
        if i == 0 and c == "-":
            strout += c
        elif c.isdigit():
            if c != "0":
                leadingzeros = False
            if not leadingzeros:
                strout += c
            else:
                nbleadingzeros += 1

    if leadingzeros and nbleadingzeros > 0:
        strout += "0"
    return strout


def check_strfloat(strin: str) -> str:
    """Takes a string and removes characters that don't belong
    in a signed floating point number.

    >>> check_strfloat("")
    ""
    >>> check_strfloat("-")
    "-"
    >>> check_strfloat("-m08.0.2")
    "-8.02"

    Args:
        strin (str): string to process to a float

    Returns:
        str: processed string
    """
    sign = ""
    if strin == "":
        return ""
    if strin[0] == "-":
        sign = "-"
    return sign + check_strfloat_pos(strin)


def check_strfloat_pos(strin: str) -> str:
    """Takes a string and removes characters that don't belong
    in a positive floating point number.

    >>> check_strfloat("")
    ""
    >>> check_strfloat("-")
    ""
    >>> check_strfloat("-m08.0.2")
    "8.02"

    Args:
        strin (str): string to process to a float

    Returns:
        str: processed string
    """
    integer = ""
    dot = ""
    decimal = ""
    isdot = False
    for c in strin:
        if c.isdigit():
            if isdot is False:
                integer += c
            if isdot is True:
                decimal += c
        if c == "." and isdot is False:
            dot = "."
            isdot = True
    if integer != "":
        integer = "{:d}".format(int(integer))
    if decimal != "":
        decimal = "{:d}".format(int(decimal[::-1]))[::-1]
    return integer + dot + decimal
