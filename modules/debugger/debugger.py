import ctypes
import thread
import threading
import time
import sys
import functools
import shlex
import traceback
import inspect

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

debugger_state = 'run'
thread_stops = {}
current_thread = None
step_notify = threading.Condition()

def is_debugger_stdio_code(code):
    In = type(sys.stdin)
    Out = type(sys.stdout)

    for T in (In, Out):
        for prop_name in dir(T):
            if prop_name.startswith('__') and prop_name != '__getattr__':
                continue
            prop = getattr(T, prop_name)
            if hasattr(prop, 'im_func'):
                 if code is prop.im_func.func_code:
                    return True
    return False

def debugger_tracer(frame, event, arg):
    global debugger_state

    if debugger_state == 'run':
        return debugger_tracer

    if is_debugger_stdio_code(frame.f_code):
        return debugger_tracer

    thread_id = get_ident()
    cv = thread_stops[thread_id]

    if debugger_state == 'stepping' and current_thread == thread_id:
        with step_notify:
            step_notify.notify()
        debugger_state = 'stop'

    while debugger_state != 'run':
        while debugger_state == 'stop' or (debugger_state == 'step' and current_thread != thread_id):
            with cv:
                cv.wait()
        if debugger_state == 'step' and current_thread == thread_id:
            debugger_state = 'stepping'
            break

    return debugger_tracer

def is_debugger_frame(frame):
    f = frame

    while f:
        if f.f_code is debugger_tracer.func_code:
            return True
        f = f.f_back

    return is_debugger_stdio_code(frame.f_code)

def execute_cmd(cmd, args, debugger_tid):
    global current_thread
    global debugger_state

    if cmd == 'threads':
        for tid in thread_stops.keys():
            mark = '   '
            if tid == current_thread:
                mark = ' * '
            print('%s%d' % (mark, tid))
    elif cmd == 'thr' or cmd == 'thread':
        tid = int(args[0])
        if tid not in thread_stops:
            print("Unknown thread id")
            return
        current_thread = tid
    elif cmd == 'stop':
        debugger_state = 'stop'
    elif cmd == 'c' or cmd == 'cont' or cmd == 'continue':
        debugger_state = 'run'
        for stop in thread_stops.values():
            with stop:
                stop.notify()
    elif cmd == 'step':
        if debugger_state != 'stop':
            print('stepping does not make sence until program is stopped')
            return
        debugger_state = 'step'
        cv = thread_stops[current_thread]
        with cv:
            cv.notify()
        while True:
            with step_notify:
                step_notify.wait()
                if debugger_state != 'stepping':
                    break
    elif cmd == 'bt' or cmd == 'backtrace':
        frame = sys._current_frames()[current_thread]
        while is_debugger_frame(frame) and frame.f_back:
            frame = frame.f_back
        traceback.print_stack(frame)


def run_debugger():
    global current_thread

    current_thread_id = get_ident()

    print('debugger_thread', current_thread_id)

    thread_ids = sys._current_frames().keys()

    for tid in thread_ids:
        if tid != current_thread_id:
            thread_stops[tid] = threading.Condition()

    current_thread = next(iter(thread_stops.keys()))

    trace_all_threads(debugger_tracer)

    while True:
        cmd_line = raw_input('debugger> ')
        cmd_parts = shlex.split(cmd_line)
        if len(cmd_parts) == 0:
            continue
        cmd = cmd_parts[0]
        args = cmd_parts[1:]
        try:
            execute_cmd(cmd, args, current_thread_id)
        except:
            traceback.print_exc()