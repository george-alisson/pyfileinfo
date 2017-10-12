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


class FileAttributes:
    '''
    Define values of file attributes
    '''
    ReadOnly = 0x1
    Hidden = 0x2
    System = 0x4
    Directory = 0x10
    Archive = 0x20
    Device = 0x40
    Normal = 0x80
    Temporary = 0x100
    SparseFile = 0x200
    ReparsePoint = 0x400
    Compressed = 0x800
    Offline = 0x1000
    NotContentIndexed = 0x2000
    Encrypted = 0x4000
    Virtual = 0x10000

    @property
    def value(self):
        '''
        type: int
        Represents the bitwise combination of the enumeration FileAttributes values.
        '''
        return self.__attribs

    def __init__(self, attribs):
        self.__attribs = attribs

    def __invert__(self):
        return FileAttributes(~self.value)

    def __or__(self, other):
        if isinstance(other, FileAttributes):
            return FileAttributes(self.value | other.value)
        elif isinstance(other, int):
            return FileAttributes(self.value | other)
        else:
            raise NotSupportedException()

    def __and__(self, other):
        if isinstance(other, FileAttributes):
            return FileAttributes(self.value & other.value)
        elif isinstance(other, int):
            return FileAttributes(self.value & other)
        else:
            raise NotSupportedException()

    def __xor__(self, other):
        return self & ~ other

    def __add__(self, other):
        return self | other

    def __sub__(self, other):
        return self & ~ other

    def __repr__(self):
        ret = []
        if self.__attribs & self.ReadOnly:
            ret += ["FileAttributes.ReadOnly"]
        if self.__attribs & self.Hidden:
            ret += ["FileAttributes.Hidden"]
        if self.__attribs & self.System:
            ret += ["FileAttributes.System"]
        if self.__attribs & self.Directory:
            ret += ["FileAttributes.Directory"]
        if self.__attribs & self.Archive:
            ret += ["FileAttributes.Archive"]
        if self.__attribs & self.Device:
            ret += ["FileAttributes.Device"]
        if self.__attribs & self.Normal:
            ret += ["FileAttributes.Normal"]
        if self.__attribs & self.Temporary:
            ret += ["FileAttributes.Temporary"]
        if self.__attribs & self.SparseFile:
            ret += ["FileAttributes.SparseFile"]
        if self.__attribs & self.ReparsePoint:
            ret += ["FileAttributes.ReparsePoint"]
        if self.__attribs & self.Compressed:
            ret += ["FileAttributes.Compressed"]
        if self.__attribs & self.Offline:
            ret += ["FileAttributes.Offline"]
        if self.__attribs & self.NotContentIndexed:
            ret += ["FileAttributes.NotContentIndexed"]
        if self.__attribs & self.Encrypted:
            ret += ["FileAttributes.Encrypted"]
        if self.__attribs & self.Virtual:
            ret += ["FileAttributes.Virtual"]
        return " | ".join(ret)


class DirectorySearchOption:
    '''
    Define values for the DirectorySearch
    '''
    TopDirectoryOnly = 0
    AllDirectories = 1


class SecurityInformation:
    '''
    Define values for SecurityInformation
    '''
    Owner = 0x1
    Group = 0x2
    Dacl = 0x4
    Sacl = 0x8
    Label = 0x10
    Attribute = 0x20
    Scope = 0x40
    Backup = 0x10000
    UnprotectedSacl = 0x10000000
    UnprotectedDacl = 0x20000000
    ProtectedSacl = 0x40000000
    ProtectedDacl = 0x80000000

    @property
    def value(self):
        '''
        type: int
        Represents the bitwise combination of the enumeration SecurityInformation values.
        '''
        return self.__info

    def __init__(self, info):
        self.__info = info

    def __invert__(self):
        return SecurityInformation(~self.value)

    def __or__(self, other):
        if isinstance(other, SecurityInformation):
            return SecurityInformation(self.value | other.value)
        elif isinstance(other, int):
            return SecurityInformation(self.value | other)
        else:
            raise NotSupportedException()

    def __and__(self, other):
        if isinstance(other, SecurityInformation):
            return SecurityInformation(self.value & other.value)
        elif isinstance(other, int):
            return SecurityInformation(self.value & other)
        else:
            raise NotSupportedException()

    def __xor__(self, other):
        return self & ~ other

    def __add__(self, other):
        return self | other

    def __sub__(self, other):
        return self & ~ other

    def __repr__(self):
        ret = []
        if self.__info & self.Owner:
            ret += ["SecurityInformation.Owner"]
        if self.__info & self.Group:
            ret += ["SecurityInformation.Group"]
        if self.__info & self.Dacl:
            ret += ["SecurityInformation.Dacl"]
        if self.__info & self.Sacl:
            ret += ["SecurityInformation.Sacl"]
        if self.__info & self.Label:
            ret += ["SecurityInformation.Label"]
        if self.__info & self.Attribute:
            ret += ["SecurityInformation.Attribute"]
        if self.__info & self.Scope:
            ret += ["SecurityInformation.Scope"]
        if self.__info & self.Backup:
            ret += ["SecurityInformation.Backup"]
        if self.__info & self.UnprotectedSacl:
            ret += ["SecurityInformation.UnprotectedSacl"]
        if self.__info & self.UnprotectedDacl:
            ret += ["SecurityInformation.UnprotectedDacl"]
        if self.__info & self.ProtectedSacl:
            ret += ["SecurityInformation.ProtectedSacl"]
        if self.__info & self.ProtectedDacl:
            ret += ["SecurityInformation.ProtectedDacl"]
        return " | ".join(ret)
