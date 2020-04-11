import os
import json
import tempfile
import threading

from pipe import pipe_function

class UnidirectionalPipeTransport(object):
    PREFIX = 'pystolpipe'

    def __init__(self):
        self.path = tempfile.mktemp(prefix=self.PREFIX)
        os.mkfifo(self.path)
        os.chmod(self.path, 0o666)
        self.__file = None

    def open_file(self, mode):
        self.__file = open(self.path, mode)

    def _pipe_in_thread(self, args):
        self.thread = threading.Thread(target=pipe_function, args=args)
        self.thread.daemon = True
        self.thread.start()

    def pipe_from(self, f, buffering):
        self._pipe_in_thread(args=(f, self.__file, buffering))

    def pipe_to(self, f, buffering):
        self._pipe_in_thread(args=(self.__file, f, buffering))

    def write(self, data):
        return self.__file.write(data)

    def readline(self):
        return self.__file.readline()

    def flush(self):
        return self.__file.flush()

    def delete_file(self):
        os.unlink(self.path)

class BidirectionalPipeTransport(object):
    def __init__(self):
        self.in_transport = UnidirectionalPipeTransport()
        self.out_transport = UnidirectionalPipeTransport()

    def send(self, s):
        self.in_transport.write(str(len(s)) + '\n')
        self.in_transport.write(s)
        self.in_transport.flush()

    def recv(self):
        return json.loads(self.out_transport.readline())

    def open_files(self):
        self.in_transport.open_file('w')
        self.out_transport.open_file('r')

    def delete_files(self):
        self.in_transport.delete_file()
        self.out_transport.delete_file()