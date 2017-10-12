"""
	fileinfo.py

	Emulate the .NET class FileInfo in Python, using Python own modules (and win32api for some mothods).

	@copyright: 2009-2017 George de Oliveira <george.alisson[at]gmail.com>
	@license: MIT License.

	Permission is hereby granted, free of charge, to any person
	obtaining a copy of this software and associated documentation
	files (the "Software"), to deal in the Software without
	restriction, including without limitation the rights to use,
	copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the
	Software is furnished to do so, subject to the following
	conditions:

	The above copyright notice and this permission notice shall be
	included in all copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
	EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
	OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
	NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
	HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
	WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
	FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
	OTHER DEALINGS IN THE SOFTWARE.
"""

import os
import shutil
import stat
import fnmatch
import datetime
from .exceptions import *
from .helpers import *

if os.name == 'nt':
    fnmatch.translate = translate


class FileInfo(object):
    '''
    FileInfo(path) -> FileInfo object
    Initializes a new instance of the FileInfo class, which acts as a wrapper for a file path.
    '''

    #-------------------- Constructor ---------------------------
    def __init__(self, path):
        '''
        Create and return a new object.  See help(type) for accurate signature.
        '''
        if isinstance(path, str):
            if self.__is_valid_path(path):
                self.__path = path
            else:
                raise InvalidPathException("'%s' is not a valid path" % path)
        else:
            raise NotSupportedException("'path' should be a string or unicode")

    #----------------------- Methods ------------------------------
    @staticmethod
    def __is_valid_path(path):
        for c in '*?"<>|':
            if c in path:
                return False
        if ":" in path and path.rindex(":") != 1:
            return False
        return bool(path)

    def __repr__(self):
        '''
        Returns repr(x).
        '''
        return 'FileInfo(r"%s")' % self.original_path

    def __eq__(self, other):
        '''
        Returns self==other.
        '''
        if isinstance(other, FileInfo):
            return os.path.samefile(self.full_path, other.full_path)
        return False

    def __iter__(self):
        '''
        Implement iter(self).
        '''
        return self.iter_items()

    def __len__(self):
        '''
        Return len(self).
        '''
        if self.is_directory:
            return self.get_directory_length()
        else:
            return self.length

    def __str__(self):
        '''
        Returns the path as a string.
        '''
        return self.full_path

    def append_text(self):
        '''
        fi.append_text() -> file object
        Return a file object that appends text to the file represented by this instance of the FileInfo (opened in 'a+' mode).
        '''
        if os.path.isfile(self.original_path):
            if os.path.exists(self.original_path):
                return open(self.original_path, "a+")
            raise FileNotFoundException("'%s' not found" % self.original_path)
        raise UnauthorizedAccessException("'%s' is not a file" % self.original_path)

    def copy_to(self, location, overwrite=False):
        '''
        fi.copy_to(location, overwrite) -> FileInfo object
        Copies an existing file or directory to a new file or directory, allowing the overwriting of an existing file or directory.
        'overwrite' defaults to False.
        '''
        if os.path.exists(self.original_path):
            if not self.__is_valid_path(location):
                raise InvalidPathException("'%s' is not valid path" % location)
            if os.path.isfile(self.original_path):
                if (overwrite) or (not os.path.exists(location)):
                    shutil.copyfile(self.original_path, location)
                    return FileInfo(location)
                raise FileAlreadyExistsException("'%s' already exists" % location)
            elif os.path.isdir(self.original_path):
                if os.path.exists(location):
                    if overwrite:
                        shutil.rmtree(location)
                        shutil.copytree(self.original_path, location)
                        return FileInfo(location)
                    else:
                        raise DirectoryAlreadyExistsException("'%s' already exists" % location)
                else:
                    shutil.copytree(self.original_path, location)
                    return FileInfo(location)
            else:
                raise NotSupportedException("'%s' can't be copied" % self.original_path)
        else:
            raise DirectoryNotFoundException("'%s' not found" % self.original_path)

    def create(self):
        '''
        fi.create() -> file object
        Return a file object represented by this instance of the FileInfo (opened in 'wb+' mode).
        '''
        if not os.path.exists(self.original_path):
            return open(self.original_path, 'wb+')
        raise FileAlreadyExistsException("'%s' already exists" % self.original_path)

    def create_text(self):
        '''
        fi.create_text() -> file object
        Return a file object represented by this instance of the FileInfo (opened in 'w+' mode).
        '''
        if not os.path.exists(self.original_path):
            return open(self.original_path, 'w+')
        raise FileAlreadyExistsException("'%s' already exists" % self.original_path)

    def create_directory(self):
        '''
        fi.create_directory() -> None
        Create a directory represented by this instance of the FileInfo.
        '''
        if not os.path.exists(self.original_path):
            os.mkdir(self.original_path)
        else:
            raise DirectoryAlreadyExistsException("'%s' already exists" % self.original_path)

    def decrypt(self):
        '''
        fi.decrypt() -> None
        Decrypts a file that was encrypted by the current account using the Encrypt method.
        This method is win32 only.
        '''
        try:
            import win32file
        except:
            raise NotSupportedException("this method is win32 only")
        win32file.DecryptFile(self.original_path)

    def delete(self):
        '''
        fi.delete() -> None
        Permanently deletes a file or directory.
        '''
        if os.path.exists(self.original_path):
            if os.path.isfile(self.original_path):
                os.remove(self.original_path)
            elif os.path.isdir(self.original_path):
                os.rmdir(self.original_path)
            else:
                raise NotSupportedException("'%s' can't be removed" % self.original_path)
        else:
            raise DirectoryNotFoundException("'%s' not found" % self.original_path)

    def delete_tree(self, ignoreerros=False, onerror=None):
        '''
        fi.delete_tree() -> None
        Permanently deletes a directory tree.
        '''
        if os.path.exists(self.original_path):
            if os.path.isdir(self.original_path):
                if onerror is None:
                    def onerror(func, path, exc_info):
                        if not os.access(path, os.W_OK):
                            os.chmod(path, stat.S_IWUSR)
                            func(path)
                        else:
                            raise
                shutil.rmtree(self.original_path, ignoreerros, onerror)
            else:
                raise NotSupportedException("'%s' can't be removed" % self.original_path)
        else:
            raise DirectoryNotFoundException("'%s' not found" % self.original_path)

    def encrypt(self):
        '''
        fi.encrypt() -> None
        Encrypts a file so that only the account used to encrypt the file can decrypt it.
        This method is win32 only.
        '''
        try:
            import win32file
        except:
            raise NotSupportedException("this method is win32 only")
        win32file.EncryptFile(self.original_path)

    def get_access_control(self, information=SecurityInformation.Owner | SecurityInformation.Group | SecurityInformation.Dacl):
        '''
        fi.get_access_control([information]) -> int or a SECURITY object
        Gets a string thats represent the access control for the file or directory described by the current FileInfo object.
        If non-WinNT system, return os.stat() of self.original_path, else return a win32security SECURITY object, returned by GetFileSecurity(self.original_path, information) api function
        'information' defaults to SecurityInformation.Owner | SecurityInformation.Group | SecurityInformation.Dacl
        '''
        if os.path.exists(self.original_path):
            if os.name != "nt":
                return os.stat(self.original_path)
            else:
                try:
                    import win32security
                except:
                    raise NotSupportedException("you need pywin modules")
                try:
                    return win32security.GetFileSecurity(self.original_path, information)
                except win32security.error as err:
                    raise UnauthorizedAccessException(err)
        raise FileNotFoundException("'%s' not found" % self.original_path)

    def get_access_control_string(self, information=SecurityInformation.Owner | SecurityInformation.Group | SecurityInformation.Dacl):
        '''
        fi.get_access_control_string([information]) -> int or a SECURITY string
        Gets a string thats represent the access control for the file or directory described by the current FileInfo object.
        If non-WinNT system, return os.stat() of self.original_path, else return SECURITY string, returned by GetFileSecurity(self.original_path, information) api function
        'information' defaults to SecurityInformation.Owner | SecurityInformation.Group | SecurityInformation.Dacl
        '''
        if os.path.exists(self.original_path):
            if os.name != "nt":
                return os.stat(self.original_path)
            else:
                try:
                    import win32security
                except:
                    raise NotSupportedException("you need pywin modules")
                try:
                    security = win32security.GetFileSecurity(self.original_path, information)
                    return win32security.ConvertSecurityDescriptorToStringSecurityDescriptor(security, win32security.SDDL_REVISION_1, information)
                except win32security.error as err:
                    raise UnauthorizedAccessException(err)
        raise FileNotFoundException("'%s' not found" % self.original_path)

    def set_access_control(self, security, information=SecurityInformation.Owner | SecurityInformation.Group | SecurityInformation.Dacl):
        '''
        fi.set_access_control(security, [infomarion]) -> None
        Applies access control described by a win32security SECURITY object to the file described by the current FileInfo object.
        If non-WinNT system, sets os.chmode(), os.chown(), os.chflags() to security, else use SetFileSecurity(self.original_path, information, security) api function, with security as a SECURITY object
        'information' defaults to SecurityInformation.Owner | SecurityInformation.Group | SecurityInformation.Dacl
        '''
        if os.path.exists(self.original_path):
            if os.name != "nt":
                if information & 0x1:
                    os.chmod(self.original_path, security.st_mode)
                if information & 0x2:
                    os.chown(self.original_path,
                             security.st_uid, security.st_gid)
                if information & 0x4:
                    os.chflags(self.original_path, security.st_flags)
            else:
                try:
                    import win32security
                except:
                    raise NotSupportedException("you need pywin modules")
                try:
                    win32security.SetFileSecurity(self.original_path, information, security)
                except win32security.error as err:
                    raise UnauthorizedAccessException(err)
        else:
            raise FileNotFoundException("'%s' not found" % self.original_path)

    def set_access_control_string(self, security, information=SecurityInformation.Owner | SecurityInformation.Group | SecurityInformation.Dacl):
        '''
        fi.set_access_control_string(security, [infomarion]) -> None
        Applies access control described by a SECURITY string to the file described by the current FileInfo object.
        If non-WinNT system, sets os.chmode(), os.chown(), os.chflags() to security, else use SetFileSecurity(self.original_path, information, security) api function, with security as a SECURITY string
        'information' defaults to SecurityInformation.Owner | SecurityInformation.Group | SecurityInformation.Dacl
        '''
        if os.path.exists(self.original_path):
            if os.name != "nt":
                if information & 0x1:
                    os.chmod(self.original_path, security.st_mode)
                if information & 0x2:
                    os.chown(self.original_path,
                             security.st_uid, security.st_gid)
                if information & 0x4:
                    os.chflags(self.original_path, security.st_flags)
            else:
                try:
                    import win32security
                except:
                    raise NotSupportedException("you need pywin modules")
                try:
                    security = win32security.ConvertStringSecurityDescriptorToSecurityDescriptor(security, win32security.SDDL_REVISION_1)
                    win32security.SetFileSecurity(self.original_path, information, security)
                except win32security.error as err:
                    raise UnauthorizedAccessException(err)
        else:
            raise FileNotFoundException("'%s' not found" % self.original_path)

    def move_to(self, location):
        '''
        fi.move_to() -> None
        Moves a specified file or directory to a new location, providing the option to specify a new file name.
        '''
        if os.path.exists(self.original_path):
            if not self.__is_valid_path(location):
                raise InvalidPathException("'%s' is not valid path" % location)
            if not os.path.exists(location):
                os.rename(self.original_path, self.original_path)
                shutil.move(self.original_path, location)
                self.__path = location
            else:
                raise DirectoryAlreadyExistsException("'%s' already exists" % location)
        else:
            raise DirectoryNotFoundException("'%s' not found" % self.original_path)

    def open(self, flags="rb+", buffersize=-1):
        '''
        fi.open(flags, buffersize) -> file object
        Opens a file with various read/write privileges.

        'flags' defaults to "rb+" and 'buffersize' to -1 (system default).
        '''
        if os.path.isfile(self.original_path) or not os.path.exists(self.original_path):
            return open(self.original_path, flags, buffersize)
        raise UnauthorizedAccessException("'%s' is not a file" % self.original_path)

    def open_shared(self, flags="rb+", sharemode="a", buffersize=-1):
        '''
        fi.open_shared(flags, sharemode, buffersize) -> file object
        Opens a file with various read/write privileges.

        Uses ctypes for share mode options and low level flags in Windows (using msvcrt._sopen()).
        'flags' first char must be:
                "r" (read - opens a existing file for reading),
                "w" (write - opens an existing file or creates a new file for writing; if it already exists, overwrite it),
                "a" (append - opens an existing file or creates a new file for writing; if it already exists, data will be written to the end of the file),
                "c" (create - always creates a new file for writing; if it already exists, an exception is thrown)
                "o" (open - opens an existing file or creates a new file for reading) or
                "t" (truncate - opens an existing file for writing and truncate it).
        Other options for 'flags':
                "+" (read and write - will be able to read and write to the file)
                "b" (binary - read and write the data 'as is', without trying to translate linefeeds and/or caradige-returns)
                "u" (utf-8 - open the file in Unicode UTF-8 mode if the file does not have an UTF-16LE BOM mark)
                "U" (utf-16 - open the file in Unicode UTF-16LE mode if the file does not have an UTF-8 BOM mark)
                "W" (widechar - open the file in Unicode UTF-16 mode if the file does not have an UTF-16LE or UTF-8 BOM mark)
                "S" (sequential - specifies primarily sequential access from disk)
                "R" (random - specifies primarily random access from disk)
                "T" (temporary - create a file as temporary and if possible do not flush to disk; must be used when creating a file)
                "D" (disk temporary - create a file as temporary; the file is deleted when the last file descriptor is closed)
                "N" (no inherit - prevents creation of a shared file descriptor).
        'sharemode' can be:
                "a" (allow read/write - deny none),
                "r" (deny read - allow write),
                "w" (deny write - allow read),
                "d" (deny read/write - allow none) or
                "s" (secure share - allow read if open for read-only).
        'flags' defaults to "rb+", sharemode to "a" (allow all), and 'buffersize' to -1 (system default).
        '''
        if os.path.isfile(self.original_path) or not os.path.exists(self.original_path):
            if os.name == 'nt':
                delete = not os.path.exists(self.original_path)
                mode = 0
                # open mode: read, write, append, create
                if flags[0] == "r":
                    mode = os.O_RDONLY
                elif flags[0] == "w":
                    mode = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
                elif flags[0] == "a":
                    mode = os.O_CREAT | os.O_WRONLY | os.O_APPEND
                elif flags[0] == "c":
                    mode = os.O_CREAT | os.O_WRONLY | os.O_EXCL
                    flags = flags.replace("c", "w")
                elif flags[0] == "o":
                    mode = os.O_CREAT | os.O_RDONLY
                    flags = flags.replace("o", "r")
                elif flags[0] == "t":
                    mode = os.O_WRONLY | os.O_TRUNC
                    flags = flags.replace("t", "w")
                else:
                    raise TypeError("Invalid file open mode. Should be \"r\" (read), \"w\" (write)(\"a\" (append) or \"c\" (create)")

                # read/write access
                if "+" in flags:
                    mode = (mode & ~os.O_WRONLY | os.O_RDWR)

                # translate options
                if "b" in flags:
                    mode |= os.O_BINARY
                elif "u" in flags:
                    mode |= 0x40000  # _O_U8TEXT
                    flags = flags.replace("u", "")
                elif "U" in flags:
                    mode |= 0x20000  # _O_U16TEXT
                    flags = flags.replace("U", "")
                elif "W" in flags:
                    mode |= 0x10000  # _O_WTEXT
                    flags = flags.replace("W", "")
                else:
                    mode |= os.O_TEXT

                # low level flags
                if 'S' in flags:
                    mode |= os.O_SEQUENTIAL
                    flags = flags.replace("S", "")
                if 'R' in flags:
                    mode |= os.O_RANDOM
                    flags = flags.replace("R", "")
                if 'T' in flags:
                    mode |= os.O_SHORT_LIVED
                    flags = flags.replace("T", "")
                if 'D' in flags:
                    mode |= os.O_TEMPORARY
                    flags = flags.replace("D", "")
                if 'N' in flags:
                    mode |= os.O_NOINHERIT
                    flags = flags.replace("N", "")

                # share mode flags
                if sharemode == "a":
                    shmode = 0x40  # _SH_DENYNO
                elif sharemode == "w":
                    shmode = 0x20  # _SH_DENYWR
                elif sharemode == "r":
                    shmode = 0x30  # _SH_DENYRD
                elif sharemode == "d":
                    shmode = 0x10  # _SH_DENYRW
                elif sharemode == "s":
                    if mode & (os.O_WRONLY | os.O_RDWR):
                        shmode = 0x10  # _SH_DENYRW
                    else:
                        shmode = 0x20  # _SH_DENYWR
                else:
                    raise TypeError("'sharemode' should be \"a\" (allow read/write), \"r\" (deny read), \"w\" (deny write)(\"d\" (deny read/write) or \"s\" (secure share)")
                import ctypes
                msvcrt = ctypes.cdll[ctypes.util.find_msvcrt()]
                sopen = msvcrt._sopen
                sopen.argtypes = (ctypes.c_char_p, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int)
                fd = sopen(self.original_path, mode, shmode,
                           stat.S_IREAD | stat.S_IWRITE)
                if fd == -1:
                    raise ctypes.WinError()
                try:
                    return os.fdopen(fd, flags, buffersize)
                except Exception as err:
                    msvcrt._close(fd)
                    if delete:
                        os.remove(self.original_path)
                    if isinstance(err, OSError):
                        err.strerror += ": (fd=%i, mode=%i, shmode=%i)" % (fd,
                                                                           mode, shmode)
                        err.filename = self.original_path
                    raise err
            else:
                raise NotSupportedException("share mode options is win32 only")
        raise UnauthorizedAccessException("'%s' is not a file" % self.original_path)

    def open_text(self):
        '''
        fi.open_text -> file object
        Creates a file object that reads from an existing text file (opened in 'r+' mode).
        '''
        if os.path.isfile(self.original_path):
            if os.path.exists(self.original_path):
                return open(self.original_path, "r+")
            raise FileNotFoundException("'%s' not found" % self.original_path)
        raise UnauthorizedAccessException("'%s' is not a file" % self.original_path)

    def open_unicode_text(self, flags="r+", encoding="UTF-8", errors='strict', buffering=1):
        '''
        fi.open_unicode_text(flags, encoding, errors, buffering) <--> codecs.open(fi.original_path, flags, encoding, errors, buffering)
        Creates a file object that reads from an existing unicode text file,
        'flags' defaults to "r+", 'encoding' to "UTF-8", 'errors' to "strict", and buffering to 1.
        '''
        if os.path.isfile(self.original_path) or not os.path.exists(self.original_path):
            import codecs
            return codecs.open(self.original_path, flags, encoding, errors, buffering)
        raise UnauthorizedAccessException("'%s' is not a file" % self.original_path)

    def open_read(self):
        '''
        fi.open_read() -> file object
        Creates a read-only file object (opened in 'rb' mode).
        '''
        if os.path.isfile(self.original_path):
            if os.path.exists(self.original_path):
                return open(self.original_path, "rb")
            raise FileNotFoundException("'%s' not found" % self.original_path)
        raise UnauthorizedAccessException("'%s' is not a file" % self.original_path)

    def open_write(self):
        '''
        fi.open_write() -> file object
        Creates a write-only file object (opened in 'ab' mode).
        '''
        if os.path.isfile(self.original_path):
            if os.path.exists(self.original_path):
                return open(self.original_path, "ab")
            raise FileNotFoundException("'%s' not found" % self.original_path)
        raise UnauthorizedAccessException("'%s' is not a file" % self.original_path)

    def replace(self, file, backup):
        '''
        fi.replace(file, backup) -> None
        Replaces the contents of a specified file with the file described by the current FileInfo object, deleting the original file, and creating a backup of the replaced file.
        '''
        if os.path.exists(file):
            if not self.__is_valid_path(backup):
                raise InvalidPathException("'%s' is not valid path" % backup)
            if not os.path.exists(backup):
                shutil.move(file, backup)
                self.move_to(file)
            else:
                raise FileAlreadyExistsException("'%s' already exists" % backup)
        else:
            raise FileNotFoundException("'%s' not found" % file)

    def create_subdirectory(self, dirname):
        '''
        fi.create_subdirectory -> FileInfo object
        Creates a subdirectory on the specified path. The specified path must be relative to this instance of FileInfo.
        '''
        if os.path.isdir(self.original_path):
            dirname = os.path.join(self.original_path, dirname)
            if not self.__is_valid_path(dirname):
                raise InvalidPathException("'%s' is not valid path" % dirname)
            if not os.path.exists(dirname):
                os.mkdir(dirname)
                return FileInfo(dirname)
            else:
                raise DirectoryAlreadyExistsException("'%s' already exists" % dirname)
        else:
            raise NotSupportedException("'%s' is not a directory" % self.original_path)

    def create_subdirectory_tree(self, tree):
        '''
        fi.create_subdirectory_tree -> FileInfo object
        Creates a subdirectory tree on the specified path. The specified tree path must be relative to this instance of FileInfo.
        '''
        if os.path.isdir(self.original_path):
            base = self.original_path
            fi = None
            for dirname in tree.split("\\"):
                fi = FileInfo(os.path.join(base, dirname))
                if not os.path.exists(fi.full_name):
                    fi.create_directory()
                base = fi.full_name
            return fi
        else:
            raise NotSupportedException("'%s' is not a directory" % self.original_path)

    def get_directories(self, search="*", option=DirectorySearchOption.TopDirectoryOnly):
        '''
        fi.get_directories(search, option) -> list of FileInfo of the subdirectories
        Returns the subdirectories of the current directory.
        'option' should be one of the enumeration DirectorySearchOption values. Dafaults to 'TopDirectoryOnly'.
        '''
        return list(self.iter_directories(search, option))

    def get_files(self, search="*", option=DirectorySearchOption.TopDirectoryOnly):
        '''
        fi.get_files(search, option) -> list of FileInfo of the filenames
        Returns a file list from the current directory.
        'option' should be one of the enumeration DirectorySearchOption values. Dafaults to 'TopDirectoryOnly'.
        '''
        return list(self.iter_files(search, option))

    def get_items(self, search="*", option=DirectorySearchOption.TopDirectoryOnly):
        '''
        fi.get_items(search, option) -> list of FileInfo of the filenames and subdirectories
        Returns a list of files and subdirectories from the current directory.
        'option' should be one of the enumeration DirectorySearchOption values. Dafaults to 'TopDirectoryOnly'.
        '''
        return list(self.iter_items(search, option))

    def iter_directories(self, search="*", option=DirectorySearchOption.TopDirectoryOnly):
        '''
        fi.iter_directories(search, option) -> generator over subdirectories in path
        Returns a generator over subdirectories from the current directory.
        'option' should be one of the enumeration DirectorySearchOption values. Dafaults to 'TopDirectoryOnly'.
        '''
        if not os.path.isdir(self.original_path):
            raise NotSupportedException("'%s' is not a directory" % self.original_path)
        if option == DirectorySearchOption.TopDirectoryOnly:
            for name in os.listdir(self.original_path):
                if os.path.isdir(os.path.join(self.original_path, name)) and fnmatch.fnmatch(name, search):
                    yield FileInfo(os.path.join(self.original_path, name))
        elif option == DirectorySearchOption.AllDirectories:
            pathlist = [self.full_path]
            lx = 1
            while lx:
                for name in os.listdir(pathlist[0]):
                    next = os.path.join(pathlist[0], name)
                    if os.path.isdir(next):
                        if fnmatch.fnmatch(name, search):
                            yield FileInfo(next)
                        pathlist += [next]
                        lx += 1
                del pathlist[0]
                lx -= 1
        else:
            raise TypeError("invalid arguments")

    def iter_files(self, search="*", option=DirectorySearchOption.TopDirectoryOnly):
        '''
        fi.iter_files(search, option) -> generator over files in path
        Returns a generator over files from the current directory.
        'option' should be one of the enumeration DirectorySearchOption values. Dafaults to 'TopDirectoryOnly'.
        '''
        if not os.path.isdir(self.original_path):
            raise NotSupportedException("'%s' is not a directory" % self.original_path)
        if option == DirectorySearchOption.TopDirectoryOnly:
            for name in os.listdir(self.original_path):
                if os.path.isfile(os.path.join(self.original_path, name)) and fnmatch.fnmatch(name, search):
                    yield FileInfo(os.path.join(self.original_path, name))
        elif option == DirectorySearchOption.AllDirectories:
            pathlist = [self.full_path]
            lx = 1
            while lx:
                for name in os.listdir(pathlist[0]):
                    next = os.path.join(pathlist[0], name)
                    if os.path.isfile(next) and fnmatch.fnmatch(name, search):
                        yield FileInfo(next)
                    elif os.path.isdir(next):
                        pathlist += [next]
                        lx += 1
                del pathlist[0]
                lx -= 1
        else:
            raise TypeError("invalid arguments")

    def iter_items(self, search="*", option=DirectorySearchOption.TopDirectoryOnly):
        '''
        fi.iter_items(search, option) -> generator over items in path.
        Returns a generator over items from the current directory.
        'option' should be one of the enumeration DirectorySearchOption values. Dafaults to 'TopDirectoryOnly'.
        '''
        if not os.path.isdir(self.original_path):
            raise NotSupportedException("'%s' is not a directory" % self.original_path)
        if option == DirectorySearchOption.TopDirectoryOnly:
            for name in os.listdir(self.original_path):
                if fnmatch.fnmatch(name, search):
                    yield FileInfo(os.path.join(self.original_path, name))
        elif option == DirectorySearchOption.AllDirectories:
            pathlist = [self.full_path]
            lx = 1
            while lx:
                for name in os.listdir(pathlist[0]):
                    next = os.path.join(pathlist[0], name)
                    if fnmatch.fnmatch(name, search):
                        yield FileInfo(next)
                    if os.path.isdir(next):
                        pathlist += [next]
                        lx += 1
                del pathlist[0]
                lx -= 1
        else:
            raise TypeError("invalid arguments")

    def get_directory_length(self, option=DirectorySearchOption.TopDirectoryOnly, search="*"):
        '''
        fi.get_directory_length(option) -> int
        Returns the Length of files in a directory.
        'option' should be one of the enumeration DirectorySearchOption values. Dafaults to 'TopDirectoryOnly'.
        '''
        length = 0
        for fi in self.iter_files(search, option):
            length += fi.length
        return length

    def compare_with(self, other):
        '''
        fi.compare_with(other) -> True if equals, False otherwise.
        Compare the path in FileInfo with a file in other path or FileInfo, or compare the common files in two directories.
        '''
        if os.path.exists(self.original_path):
            if isinstance(other, FileInfo):
                other = other.full_path
            if os.path.exists(other):
                import filecmp
                if os.path.isfile(self.original_path):
                    return filecmp.cmp(self.original_path, other)
                elif os.path.isdir(self.original_path):
                    if os.path.isdir(other):
                        commfiles = filecmp.dircmp(self.original_path, other).common_files
                        return bool(commfiles) and (filecmp.cmpfiles(self.original_path, other, commfiles)[0] == commfiles)
                    else:
                        return False
                else:
                    raise NotSupportedException("'%s' is not a file or directory" % self.original_path)
            else:
                raise DirectoryNotFoundException("'%s' not found" % other)
        else:
            raise DirectoryNotFoundException("'%s' not found" % self.original_path)

    def compress(self):
        '''
        fi.compress() -> None
        Compress a file or directory on a volume whose file system supports per-file and per-directory compression.
        This method is win32 only.
        '''
        try:
            import win32file
            import ctypes
        except:
            raise NotSupportedException("this method is win32 only")
        if not os.path.exists(self.original_path):
            raise FileNotFoundException("'%s' not found" % self.original_path)
        if self.is_read_only:
            raise UnauthorizedAccessException("'%s' is readonly." % self.original_path)
        hFile = win32file.CreateFile(self.full_path, win32file.GENERIC_READ | win32file.FILE_GENERIC_WRITE,
                                     win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE, None, win32file.OPEN_EXISTING,
                                     win32file.FILE_FLAG_BACKUP_SEMANTICS, 0)
        win32file.DeviceIoControl(hFile, 0x9c040, ctypes.c_ushort(1), 0)
        win32file.CloseHandle(hFile)

    def uncompress(self):
        '''
        fi.uncompress() -> None
        Uncompress a file or directory on a volume whose file system supports per-file and per-directory compression.
        This method is win32 only.
        '''
        try:
            import win32file
            import ctypes
        except:
            raise NotSupportedException("this method is win32 only")
        if not os.path.exists(self.original_path):
            raise FileNotFoundException("'%s' not found" % self.original_path)
        if self.is_read_only:
            raise UnauthorizedAccessException("'%s' is readonly." % self.original_path)
        hFile = win32file.CreateFile(self.full_path, win32file.GENERIC_READ | win32file.FILE_GENERIC_WRITE,
                                     win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE, None, win32file.OPEN_EXISTING,
                                     win32file.FILE_FLAG_BACKUP_SEMANTICS, 0)
        win32file.DeviceIoControl(hFile, 0x9c040, ctypes.c_ushort(0), 0)
        win32file.CloseHandle(hFile)

    def rename(self, name):
        '''
        fi.rename(name) -> None.
        Renames a file or directory without moving it.
        '''
        if name == self.name:
            return
        if name != os.path.basename(name):
            raise NotSupportedException("'name' must be a basename, not a path; use move_to() instead")
        name = os.path.join(self.directory_name, name)
        self.move_to(name)

    def move_to_directory(self, directory):
        '''
        fi.move_to_directory(directory) -> None.
        Moves a file or directory to a new location without renaming it.
        '''
        if directory == self.directory_name:
            return
        if os.path.isfile(directory):
            raise NotSupportedException("'directory' must be a path, not a file; use move_to() instead")
        directory = os.path.join(directory, self.name)
        self.move_to(directory)

    def copy_to_directory(self, directory, overwrite=False):
        '''
        fi.copy_to_directory(directory, overwrite) -> FileInfo object
        Copies an existing file or directory to a new location without renaming it, allowing the overwriting of an existing file or directory.
        'overwrite' defaults to False.
        '''
        if directory == self.directory_name:
            return FileInfo(self.original_path)
        if os.path.isfile(directory):
            raise NotSupportedException("'directory' must be a path, not a file; use copy_to() instead")
        directory = os.path.join(directory, self.name)
        return self.copy_to(directory, overwrite)

    def join(self, other):
        '''
        fi.join(other) -> FileInfo object
        Joins the path of the current FileInfo object to the path 'other'.
        '''
        if not os.path.isdir(self.original_path):
            raise NotSupportedException("'%s' is not a directory" % self.original_path)
        if isinstance(other, FileInfo):
            return FileInfo(os.path.join(self.full_path, other.full_path))
        return FileInfo(os.path.join(self.full_path, other))

    #------------------------ Fields ---------------------------------
    @property
    def full_path(self):
        '''
        type: str
        Represents the fully qualified path of the directory or file.
        '''
        return os.path.realpath(self.__path)

    @property
    def original_path(self):
        '''
        type: str
        The path originally specified by the user, whether relative or absolute.
        '''
        return self.__path

    #----------------- Properties ---------------------------------

    @Property
    def attributes():
        doc = \
            '''
		type: int
		Gets or sets the attributes of the current directory or file.
		Attributes sholud be a bitwise combination of the enumeration FileAttributes values.
		'''

        def fget(self):
            try:
                import win32file
            except:
                raise NotSupportedException("this method is win32 only")
            if os.path.exists(self.original_path):
                return FileAttributes(win32file.GetFileAttributes(self.original_path))
            else:
                raise DirectoryNotFoundException("'%s' not found" % self.original_path)

        def fset(self, attrib):
            try:
                import win32file
            except:
                raise NotSupportedException("this method is win32 only")
            if os.path.exists(self.original_path):
                if isinstance(attrib, FileAttributes):
                    attrib = attrib.value
                if not isinstance(attrib, int):
                    raise TypeError("Attributes should be a bitwise combination of the enumeration FileAttributes values")
                if attrib != 0:
                    if os.path.isdir(self.original_path):
                        attrib &= ~0x100
                    win32file.SetFileAttributes(self.original_path, attrib)
            else:
                raise DirectoryNotFoundException("'%s' not found" % self.original_path)
        return locals()

    @Property
    def creation_time():
        doc = \
            '''
		type: datetime
		Gets or sets the creation time of the current directory or file.
		Set is win32 only.
		'''

        def fget(self):
            if os.path.exists(self.original_path):
                return datetime.datetime.fromtimestamp(os.path.getctime(self.original_path))
            raise FileNotFoundException("'%s' not found" % self.original_path)

        def fset(self, settime):
            try:
                import win32file
                import pywintypes
                import time
            except:
                raise NotSupportedException("set is win32 only")
            if not os.path.exists(self.original_path):
                raise FileNotFoundException("'%s' not found" % self.original_path)
            if self.IsReadOnly:
                raise UnauthorizedAccessException("'%s' is readonly." % self.original_path)
            hFile = win32file.CreateFile(self.full_path, win32file.GENERIC_READ | win32file.FILE_GENERIC_WRITE,
                                         win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE, None, win32file.OPEN_EXISTING,
                                         win32file.FILE_FLAG_BACKUP_SEMANTICS, 0)
            ctime = pywintypes.Time(time.mktime(settime.timetuple()) + (settime.microsecond / 1000000.0))
            win32file.SetFileTime(hFile, ctime, None, None)
            win32file.CloseHandle(hFile)
        return locals()

    @property
    def directory(self):
        '''
        type: FileInfo
        Gets an instance of the parent directory.
        '''
        return FileInfo(self.directory_name)

    @Property
    def directory_name():
        doc = \
            '''
		type: str
		Gets or sets a string representing the directory's full path.
		'''

        def fget(self):
            return os.path.dirname(self.full_path)

        def fset(self, new):
            self.MoveToDirectory(new)
        return locals()

    @property
    def exists(self):
        '''
        type: bool
        Gets a value indicating whether a file exists.
        '''
        return os.path.exists(self.original_path)

    @Property
    def extension():
        doc = \
            '''
		type: str
		Gets or sets the string representing the extension part of the file.
		'''

        def fget(self):
            return os.path.splitext(self.full_path)[1]

        def fset(self, new):
            if not isinstance(new, basestring) or not new or new[0] != ".":
                raise TypeError("Extension should be a string or unicode starting with '.'")
            self.Rename(self.base_name + new)
        return locals()

    @Property
    def full_name():
        doc = \
            '''
		type: str
		Gets or sets the full path of the directory or file.
		'''

        def fget(self):
            return self.full_path

        def fset(self, new):
            self.MoveTo(new)
        return locals()

    @Property
    def is_read_only():
        doc = \
            '''
		type: bool
		Gets or sets a value that determines if the current file is read only.
		'''

        def fget(self):
            if os.path.exists(self.original_path):
                mode = os.stat(self.original_path)[0]
                return (mode & stat.S_IWRITE == 0) and (mode & stat.S_IREAD != 0)
            raise FileNotFoundException("'%s' not found" % self.original_path)

        def fset(self, boolean):
            if os.path.exists(self.original_path):
                if boolean:
                    return os.chmod(self.original_path, os.stat(self.original_path)[0] & ~stat.S_IWRITE | stat.S_IREAD)
                else:
                    return os.chmod(self.original_path, os.stat(self.original_path)[0] | stat.S_IWRITE | stat.S_IREAD)
            raise FileNotFoundException("'%s' not found" % self.original_path)
        return locals()

    @Property
    def last_access_time():
        doc = \
            '''
		type: datetime
		Gets or sets the time the current file or directory was last accessed.
		'''

        def fget(self):
            if os.path.exists(self.original_path):
                return datetime.datetime.fromtimestamp(os.path.getatime(self.original_path))
            raise FileNotFoundException("'%s' not found" % self.original_path)

        def fset(self, settime):
            if os.path.exists(self.original_path):
                import time
                settime = time.mktime(settime.timetuple()) + \
                    (settime.microsecond / 1000000.0)
                return os.utime(self.original_path, (settime, os.path.getmtime(self.original_path)))
            raise FileNotFoundException("'%s' not found" % self.original_path)
        return locals()

    @Property
    def last_write_time():
        doc = \
            '''
		type: datetime
		Gets or sets the time when the current file or directory was last written to.
		'''

        def fget(self):
            if os.path.exists(self.original_path):
                return datetime.datetime.fromtimestamp(os.path.getmtime(self.original_path))
            raise FileNotFoundException("'%s' not found" % self.original_path)

        def fset(self, settime):
            if os.path.exists(self.original_path):
                import time
                settime = time.mktime(settime.timetuple()) + \
                    (settime.microsecond / 1000000.0)
                return os.utime(self.original_path, (os.path.getatime(self.original_path), settime))
            raise FileNotFoundException("'%s' not found" % self.original_path)
        return locals()

    @property
    def length(self):
        '''
        type: int
        Gets the size, in bytes, of the current file.
        '''
        if os.path.exists(self.original_path):
            return os.path.getsize(self.original_path)
        raise FileNotFoundException("'%s' not found" % self.original_path)

    @Property
    def name():
        doc = \
            '''
		type: str
		Gets or sets the name of the file.
		'''

        def fget(self):
            return os.path.basename(self.full_path)

        def fset(self, new):
            self.Rename(new)
        return locals()

    @Property
    def base_name():
        doc = \
            '''
		type: str
		Gets or sets the name of the file without extension.
		'''

        def fget(self):
            return os.path.basename(os.path.splitext(self.full_path)[0])

        def fset(self, val):
            self.Rename(val + self.extension)
        return locals()

    @property
    def is_directory(self):
        '''
        type: bool
        Gets a value that determines if the path is a directory.
        '''
        return os.path.isdir(self.original_path)

    @property
    def is_file(self):
        '''
        type: bool
        Gets a value that determines if the path is a file.
        '''
        return os.path.isfile(self.original_path)

    @property
    def root(self):
        '''
        type: str
        Gets the root portion of a path.
        This attribute is win32 only.
        '''
        if os.name != 'nt':
            raise NotSupportedException("this attribute is win32 only")
        ret = os.path.splitdrive(self.full_path)[0]
        if ret:
            return ret + '\\'
        return os.path.splitunc(self.full_path)[0]

    @property
    def parent(self):
        '''
        type: str
        Gets the parent directory of a specified subdirectory (empty string if is root).
        This attribute is win32 only.
        '''
        if os.path.isdir(self.original_path):
            ret = os.path.dirname(self.full_path)
            if ret != self.root:
                return ret
            return ""
        raise NotSupportedException("'%s' is not a directory" % self.original_path)


__all__ = ["FileInfo", "FileInfoError", "FileNotFoundException", "FileAlreadyExistsException",
           "DirectoryNotFoundException", "DirectoryAlreadyExistsException", "InvalidPathException",
           "NotSupportedException", "UnauthorizedAccessException", "FileAttributes", "DirectorySearchOption",
           "SecurityInformation"]
