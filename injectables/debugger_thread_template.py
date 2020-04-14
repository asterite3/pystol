import sys, json, functools

try:
    import thread
except ImportError:
    import _thread as thread

def debugger_thread_func(saved_greenlet_stack):
    sys.stdin = LocalProxy(sys.stdin, ReplacedStdin("%s"))
    out = "%s"
    sys.stdout = LocalProxy(sys.stdout, ReplacedOut(out))
    sys.stderr = LocalProxy(sys.stderr, ReplacedOut(out))

    with open("%s") as control_in, open("%s", "w", 1) as control_out:
        def respond(data):
            control_out.write(json.dumps(data) + chr(0x0a))
        while True:
            l = int(control_in.readline())
            control_command = control_in.read(l)
            if control_command == "ping":
                respond("pong")
                continue
            namespace = {"respond": respond, "saved_greenlet_stack": saved_greenlet_stack}
            exec(control_command, namespace)

start_new_thread = thread.start_new_thread

if "gevent.monkey" in sys.modules:
    for thread_module in ["thread", "_thread"]:
        if sys.modules["gevent.monkey"].is_object_patched(thread_module, "start_new_thread"):
            start_new_thread = sys.modules["gevent.monkey"].get_original(thread_module, "start_new_thread")
            break

saved_greenlet_stack = None

if "greenlet" in sys.modules:
    import traceback
    saved_greenlet_stack = {
        "greenlet": sys.modules["greenlet"].getcurrent(),
        "stack": traceback.format_stack()[:-1]
    }

start_new_thread(debugger_thread_func, (saved_greenlet_stack,))