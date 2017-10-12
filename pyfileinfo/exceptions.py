'''
   Exeptions for FileInfo class
'''


class FileInfoError(IOError):
    '''
    Base class of FileInfo's erros
    '''
    pass


class FileNotFoundException(FileInfoError):
    '''
    The exception that is thrown when an attempt to access a file that does not exist on disk fails.
    '''
    pass


class FileAlreadyExistsException(FileInfoError):
    '''
    The exception that is thrown when the destination file already exists.
    '''
    pass


class DirectoryAlreadyExistsException(FileAlreadyExistsException):
    '''
    The exception that is thrown when the destination file or directory already exists.
    '''
    pass


class DirectoryNotFoundException(FileNotFoundException):
    '''
    The exception that is thrown when part of a file or directory cannot be found.
    '''
    pass


class NotSupportedException(FileInfoError):
    '''
    Exception for not supported operations
    '''
    pass


class InvalidPathException(FileInfoError):
    '''
    Exception for invalid paths
    '''
    pass


class UnauthorizedAccessException(IOError):
    '''
    The exception that is thrown when the operating system denies access because of an I/O error or a specific type of security error.
    '''
    pass
