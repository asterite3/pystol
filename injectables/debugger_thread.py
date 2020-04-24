import sys, json, functools

def debugger_thread_func():
    ident = get_ident()
    for builtin_module_name in ["__builtin__", "builtins"]:
        if "gevent.monkey" in sys.modules and sys.modules["gevent.monkey"].is_object_patched(builtin_module_name, "__import__"):
            real_import = sys.modules["gevent.monkey"].get_original(builtin_module_name, "__import__")
            patched_import = __import__
            def import_wrapper(*args, **kwargs):
                if get_ident() == ident:
                    return real_import(*args, **kwargs)
                return patched_import(*args, **kwargs)
            sys.modules[builtin_module_name].__import__ = import_wrapper
            break

    sys.stdin = LocalProxy(sys.stdin, ReplacedStdin(pystol_stdin))
    out = pystol_stdout
    sys.stdout = LocalProxy(sys.stdout, ReplacedOut(out))
    sys.stderr = LocalProxy(sys.stderr, ReplacedOut(out))

    try:
        with open(pystol_control_in) as control_in, open(pystol_control_out, "w", 1) as control_out:
            def respond(data):
                control_out.write(json.dumps(data) + chr(0x0a))
            while True:
                l_str = control_in.readline().strip()
                if l_str == "":
                    break
                l = int(l_str)
                control_command = control_in.read(l)
                if control_command == "ping":
                    respond("pong")
                    continue
                namespace = {
                    "respond": respond,
                    "state": state,
                    "get_ident": get_ident,
                    "allocate_lock": allocate_lock,
                    "debugger_thread_ident": ident
                }
                exec(control_command, namespace)
    finally:
        sys.stderr = sys.stderr.get_original()
        sys.stdout = sys.stdout.get_original()
        sys.stdin = sys.stdin.get_original()

state.current_thread_type = "thread"
state.current_thread = get_ident()

start_new_thread(debugger_thread_func, ())