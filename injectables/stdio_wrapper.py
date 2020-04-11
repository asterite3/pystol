class Replaced:
    def __init__(self, path, mode):
        self.path = path
        self.mode = mode
        self.f = open(self.path, self.mode, 1)
        #self.f = None
    def get_f(self):
        #if self.f is None:
        #    #self.f = open(self.path, self.mode, 1)
        return self.f
    def fileno(self):
        return self.get_f().fileno()
    def flush(self):
        return self.get_f().flush()

class ReplacedStdin(Replaced):
    def __init__(self, path):
        Replaced.__init__(self, path, "r")
    def read(self, n):
        return self.get_f().read(n)
    def readline(self):
        return self.get_f().readline()

class ReplacedOut(Replaced):
    def __init__(self, path):
        Replaced.__init__(self, path, "w")
    def write(self, s):
        res = self.get_f().write(s)
        self.f.flush()
        return res