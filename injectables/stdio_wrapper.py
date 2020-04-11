class Replaced:
    def __init__(self, path, mode):
        self.path = path
        self.mode = mode
        self._f = open(self.path, self.mode, 1)
    def fileno(self):
        return self._f.fileno()
    def flush(self):
        return self._f.flush()

class ReplacedStdin(Replaced):
    def __init__(self, path):
        Replaced.__init__(self, path, "r")
    def read(self, n):
        return self._f.read(n)
    def readline(self):
        return self._f.readline()

class ReplacedOut(Replaced):
    def __init__(self, path):
        Replaced.__init__(self, path, "w")
    def write(self, s):
        res = self._f.write(s)
        self._f.flush()
        return res