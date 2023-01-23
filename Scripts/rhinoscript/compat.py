"""python engine compatibility module.

Example:
    >>> from rhinoscript import compat
    >>> from rhinoscript.compat import IRONPY277
    >>> from rhinoscript.compat import RANGE
    >>> non_value = compat.ENUM_NONE(some_enum)
"""

import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
IRONPY273 = sys.version_info[:3] == (2, 7, 3)
IRONPY277 = sys.version_info[:3] == (2, 7, 7)
IRONPY278 = sys.version_info[:3] == (2, 7, 8)
IRONPY279 = sys.version_info[:3] == (2, 7, 9)
IRONPY2 = IRONPY273 or IRONPY277 or IRONPY278 or IRONPY279


RANGE = range
if IRONPY2:
    RANGE = xrange


STRING_TYPE = str
if IRONPY2:
    STRING_TYPE = basestring


def ITERATOR2LIST(iteratorOrList):
    """Corerce given iterator to a python list"""
    return iteratorOrList if isinstance(iteratorOrList, list) else list(iteratorOrList)


def ENUM_NONE(e):
    """Safely get None value for python2 or python3"""
    return getattr(e, 'NONE' if PY3 else 'None')


def IS_STRING_INSTANCE(s):
    """Safely check if given object is a string for python2 or python3"""
    return isinstance(s, STRING_TYPE)
