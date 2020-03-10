# -*- utf-8 -*-
#############################################
# PSF license aggrement for usebinaryfile.py
# Developed by Ivan Rybko
# UseBinaryFile
#############################################

from struct import Struct
#
class UseBinaryFile:
    def __init__(self):
        self.records = list()
        self.fmt = str()
        self.fd = None

    def write(self, **kwargs):
        """Write a sequence of tuples to a binary file of structures."""
        self.records = kwargs["records"]
        self.fmt     = kwargs["fmt"]
        self.fd      = kwargs["fdescr"]
        record_struct = Struct(self.fmt)

        for record in self.records:
            fd.write(record_struct.pack(*record))

    def read(self, **kwargs):
        """Read a binary file of structures to a sequence of tuples."""
        self.fmt     = kwargs["fmt"]
        self.fd      = kwargs["fdescr"]
        record_struct = Struct(fmt)

        chunks = iter(lambda: self.fd.read(record_struct.size), b'')
        self.records.append((record_struct.unpack(chunk) for chunk in chunks))
