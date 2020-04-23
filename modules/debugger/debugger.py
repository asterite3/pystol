import ctypes
import thread
import time
import sys

Py_tracefunc = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.py_object, ctypes.py_object, ctypes.c_int, ctypes.py_object)

class PyFrameObject(ctypes.Structure):
    pass

PyFrameObject._fields_ = [
                ('ob_refcnt',            ctypes.c_size_t),                # Py_ssize_t ob_refcnt;
                ('ob_type',              ctypes.c_void_p),                # struct _typeobject *ob_type;
                ('ob_size',              ctypes.c_size_t),                # Py_ssize_t ob_size;
                ('f_back',               ctypes.POINTER(PyFrameObject)),  # struct _frame *f_back
                ('f_code',               ctypes.c_void_p),                # PyCodeObject *f_code;
                ('f_builtins',           ctypes.py_object),               # PyObject *f_builtins;
                ('f_globals',            ctypes.py_object),               # PyObject *f_globals;
                ('f_locals',             ctypes.py_object),               # PyObject *f_locals;
                ('f_valuestack',         ctypes.c_void_p),                # PyObject **f_valuestack
                ('f_stacktop',           ctypes.c_void_p),                # PyObject **f_stacktop
                ('f_trace',              ctypes.py_object),               # PyObject *f_trace;
    ]

class PyThreadState(ctypes.Structure):
    _fields_ = [("next",                ctypes.POINTER(ctypes.c_int)),
                ("interp",              ctypes.POINTER(ctypes.c_int)),
                ('frame',               ctypes.POINTER(PyFrameObject)),
                ('recursion_depth',     ctypes.c_int),
                ('tracing',             ctypes.c_int),
                ('use_tracing',         ctypes.c_int),
                ('c_profilefunc',       Py_tracefunc),
                ('c_tracefunc',         Py_tracefunc),
                ('c_profileobj',        ctypes.py_object),
                ('c_traceobj',          ctypes.py_object),
                ('curexc_type',         ctypes.py_object),
                ('curexc_value',        ctypes.py_object),
                ('curexc_traceback',    ctypes.py_object),
                ('exc_type',            ctypes.py_object),
                ('exc_value',           ctypes.py_object),
                ('exc_traceback',       ctypes.py_object),
                ('dict',                ctypes.py_object),
                ('tick_counter',        ctypes.c_int),
                ('gilstate_counter',    ctypes.c_int),
                ('async_exc',           ctypes.py_object),
                ('thread_id',           ctypes.c_long)
                ]

def noop_tracer(_, __, ___):
    return noop_tracer

def tracer(frame, event, arg):
    print(get_ident(), 'trace', frame, event, arg)#, arg)
    return tracer


def trace_all_threads(trace_function):
    sys.settrace(noop_tracer)
    ident = thread.get_ident()

    ctypes.pythonapi.PyInterpreterState_Head.restype = ctypes.c_void_p
    interp = ctypes.pythonapi.PyInterpreterState_Head()
    ctypes.pythonapi.PyInterpreterState_ThreadHead.restype = ctypes.c_void_p
    ctypes.pythonapi.PyInterpreterState_ThreadHead.argtypes = [ctypes.c_void_p]
    t = ctypes.pythonapi.PyInterpreterState_ThreadHead(interp)
    ctypes.pythonapi.PyThreadState_Next.restype = ctypes.c_void_p
    ctypes.pythonapi.PyThreadState_Next.argtypes = [ctypes.c_void_p]

    empty_obj = ctypes.py_object()

    while t is not None:
        t_p = ctypes.cast(t,ctypes.POINTER(PyThreadState))
        if t_p[0].thread_id == ident:
            trace_trampoline = t_p[0].c_tracefunc
            break
        t = ctypes.pythonapi.PyThreadState_Next(t)

    t = ctypes.pythonapi.PyInterpreterState_ThreadHead(interp)

    while t is not None:
        t_p = ctypes.cast(t,ctypes.POINTER(PyThreadState))
        t_frame = t_p[0].frame
        if t_p[0].thread_id != ident:
            try:
                temp = t_p[0].c_traceobj
            except ValueError:
                temp = None
            if trace_function != empty_obj: #Py_XINCREF
                refcount = ctypes.c_long.from_address(id(trace_function))
                refcount.value += 1

            #t_p[0].c_tracefunc = ctypes.cast(None, Py_tracefunc)
            t_p[0].c_traceobj  = empty_obj
            t_p[0].use_tracing = int(t_p[0].c_profilefunc is not None)
            if temp is not None: #Py_XDECREF
                refcount = ctypes.c_long.from_address(id(temp))
                refcount.value -= 1 #don't need to dealloc since we have a ref in here and it'll always be >0
            t_p[0].c_tracefunc = trace_trampoline
            t_p[0].c_traceobj  = trace_function

            while t_frame:
                t_frame[0].f_trace = trace_function
                t_frame = t_frame[0].f_back

            t_p[0].use_tracing = 1#int((func is not None) or (t_p[0].c_profilefunc is not None))
        t = ctypes.pythonapi.PyThreadState_Next(t)

def test_tracer(frame, event, arg):
    print('trace', frame, event, arg)

def run_debugger():
    trace_all_threads(test_tracer)