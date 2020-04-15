import sys
try:
    import thread
except ImportError:
    import _thread as thread

start_new_thread = thread.start_new_thread
get_ident = thread.get_ident

if "gevent.monkey" in sys.modules:
    for thread_module in ["thread", "_thread"]:
        if sys.modules["gevent.monkey"].is_object_patched(thread_module, "start_new_thread"):
            start_new_thread = sys.modules["gevent.monkey"].get_original(thread_module, "start_new_thread")
        if sys.modules["gevent.monkey"].is_object_patched(thread_module, "get_ident"):
            get_ident = sys.modules["gevent.monkey"].get_original(thread_module, "get_ident")