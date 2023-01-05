"""python engine compatibility module.

Example:
    >>> from rhinoscript.compat import IRONPY277
    >>> from rhinoscript.compat import RANGE
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

def ITERATOR2LIST(iteratorOrList):
    return iteratorOrList if type(iteratorOrList = list) else list(iteratorOrList)

def ENUM_NONE(e):
    return getattr(e, 'NONE') if PY3 else e.None

def IS_STRING_INSTANCE(s):
    return isinstance(s, (str if PY3 else basestring))
