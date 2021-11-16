
from collections import defaultdict
import weakref
import re

regex = re.compile(r'(\(\?P\<[a-zA-Z0-9]+\>[^)]+\))')

# Useful Classes #########################################

class KeepRefs(object):
    __refs__ = defaultdict(list)
    def __init__(self):
        self.__refs__[self.__class__].append(weakref.ref(self))

    @classmethod
    def get_instances(cls):
        for inst_ref in cls.__refs__[cls]:
            inst = inst_ref()
            if inst is not None:
                yield inst

# Generic Methods #######################################


def regex_to_var(reg):
    return ''.join(
        map(lambda s: (regex.match(s) and s) or \
                s.upper().replace('/', '_').replace('-', '_'),
            regex.split(reg)
        )
    )


def regex_to_fmt(expr):
    lhs = re.compile(r'\(\?P\<')
    rhs = re.compile(r'\>[^\)]+\)')
    return rhs.sub('}', lhs.sub('{', expr))
