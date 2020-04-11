try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident

class LocalProxy:
    def __init__(self, wrapped, replacement):
        self.__wrapped = wrapped
        self.__replacement = replacement
        self.__ident = get_ident()

    def _get_current_object(self):
        if get_ident() == self.__ident:
            return self.__replacement
        return self.__wrapped

    def __getattr__(self, name):
        return getattr(self._get_current_object(), name)
