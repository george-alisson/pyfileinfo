'''
   Helpers for FileInfo class
'''

import re
from .exceptions import NotSupportedException


def Property(func):
    return property(**func())


def translate(pat):
    res = ''
    for c in pat:
        if c == '*':
            res += '.*'
        elif c == '?':
            res += '.'
        else:
            res += re.escape(c)
    return res + "$"


class Flag(object):
    '''
    Helper for flags.
    '''
    @property
    def value(self):
        '''
        type: int
        Represents the bitwise combination of the enumeration values.
        '''
        return self.__value

    def __init__(self, value):
        self.__value = value

    def __invert__(self):
        return self.__class__(~self.value)

    def __or__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.value | other.value)
        elif isinstance(other, int):
            return self.__class__(self.value | other)
        else:
            raise NotSupportedException()

    def __and__(self, other):
        if isinstance(other, FileAttributes):
            return self.__class__(self.value & other.value)
        elif isinstance(other, int):
            return self.__class__(self.value & other)
        else:
            raise NotSupportedException()

    def __xor__(self, other):
        if isinstance(other, FileAttributes):
            return self.__class__(self.value ^ other.value)
        elif isinstance(other, int):
            return self.__class__(self.value ^ other)
        else:
            raise NotSupportedException()

    def __add__(self, other):
        return self | other

    def __sub__(self, other):
        return self & ~ other

    def __eq__(self, other):
        if isinstance(other, FileAttributes):
            return self.value == other.value
        elif isinstance(other, int):
            return self.value == other
        else:
            return False

    def __repr__(self):
        keys = []
        for k, v in self._attributes.items():
            if self.__value & v:
                keys.append('{0}.{1}'.format(self.__class__.__name__, k))
        if not keys:
            raise NotSupportedException()
        return " | ".join(keys)

    @property
    def _attributes(self):
        return {k: v for k, v in self.__class__.__dict__.items()
                if not re.match('<function.*?>', str(v)) and not k.startswith('_')}


class FileAttributes(Flag):
    '''
    Define values of file attributes
    '''
    READ_ONLY = 0x1
    HIDDEN = 0x2
    SYSTEM = 0x4
    DIRECTORY = 0x10
    ARCHIVE = 0x20
    DEVICE = 0x40
    NORMAL = 0x80
    TEMPORARY = 0x100
    SPARSE_FILE = 0x200
    REPARSE_POINT = 0x400
    COMPRESSED = 0x800
    OFFLINE = 0x1000
    NOT_CONTENT_INDEXED = 0x2000
    ENCRYPTED = 0x4000
    VIRTUAL = 0x10000


class SecurityInformation(Flag):
    '''
    Define values for SecurityInformation
    '''
    OWNER = 0x1
    GROUP = 0x2
    DACL = 0x4
    SACL = 0x8
    LABEL = 0x10
    ATTRIBUTE = 0x20
    SCOPE = 0x40
    BACKUP = 0x10000
    UNPROTECTED_SACL = 0x10000000
    UNPROTECTED_DACL = 0x20000000
    PROTECTED_SACL = 0x40000000
    PROTECTED_DACL = 0x80000000


class DirectorySearchOption(object):
    '''
    Define values for the DirectorySearch
    '''
    TOP_DIRECTORY_ONLY = 0
    ALL_DIRECTORIES = 1
