"""Number patterns for formatNumber (Task 18.3.6d-2) - checked when compiling.

The same rules as the C runtime (src/codegen/c_strings.py, fusion_printf_pattern_problem /
fusion_excel_pattern_problem), which checks patterns built while the program runs. Keep the
two in step.

- A pattern starting with '%' is printf style: exactly one number conversion
  (d i f e E g G x X o) with up to 5 flags (- + space 0 #), a width and a precision of at
  most 1000; '%%' is a percent sign; text may follow the conversion. Never %s, %n, %p or *
- Any other pattern is Excel/.NET style: the number part runs from the first 0 / # to the
  last one (with a '.' just before it), holding only 0 # , and one '.'; at most 15
  decimal places; text before and after is printed as it is, and a '%' there multiplies
  the number by 100
"""

from typing import Optional


def printf_pattern_problem(pattern: str) -> Optional[str]:
    found = False
    i = 0
    while i < len(pattern):
        if pattern[i] != '%':
            i += 1
            continue
        if pattern[i + 1:i + 2] == '%':
            i += 2
            continue
        j, flags = i + 1, 0
        while j < len(pattern) and pattern[j] in '-+ 0#':
            j += 1
            flags += 1
            if flags > 5:
                return "more than 5 flags"
        start = j
        while j < len(pattern) and pattern[j].isdigit() and pattern[j] in '0123456789':
            j += 1
        if j > start and int(pattern[start:j]) > 1000:
            return "a width over 1000"
        if j < len(pattern) and pattern[j] == '.':
            j += 1
            start = j
            while j < len(pattern) and pattern[j] in '0123456789':
                j += 1
            if j > start and int(pattern[start:j]) > 1000:
                return "a precision over 1000"
        if j >= len(pattern):
            return "a '%' at the end has no conversion letter"
        if pattern[j] == '*':
            return "'*' widths aren't allowed - write the number"
        if pattern[j] not in 'difeEgGxXo':
            return "only the conversions d i f e E g G x X o are allowed"
        if found:
            return "more than one number conversion"
        found = True
        i = j + 1
    return None if found else "no number conversion such as %d or %.2f"


def excel_pattern_problem(pattern: str) -> Optional[str]:
    places = [i for i, c in enumerate(pattern) if c in '0#']
    if not places:
        return "no 0 or # digit placeholder"
    first, last = places[0], places[-1]
    if first > 0 and pattern[first - 1] == '.':
        first -= 1
    dot = False
    decimals = 0
    for c in pattern[first:last + 1]:
        if c in '0#':
            decimals += dot
        elif c == '.':
            if dot:
                return "more than one decimal point"
            dot = True
        elif c == ',':
            if dot:
                return "a ',' after the decimal point"
        else:
            return "a character other than 0 # , . inside the number part"
    if decimals > 15:
        return "more than 15 decimal places"
    return None


def number_pattern_problem(pattern: str) -> Optional[str]:
    """None for a valid formatNumber pattern, else what's wrong with it."""
    if pattern.startswith('%'):
        return printf_pattern_problem(pattern)
    return excel_pattern_problem(pattern)
