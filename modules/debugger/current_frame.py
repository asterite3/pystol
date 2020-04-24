import gc, sys

def apply_frame_offset(frame):
    offset = getattr(state, 'frame_offset', 0)
    if offset == 0:
        return frame
    stack = []
    f = frame
    while f:
        stack.append(f)
        f = f.f_back
    if offset >= len(stack):
        offset = len(stack) - 1
        state.frame_offset = offset
    return stack[offset]

def get_thread_frame():
    for ident, frame in sys._current_frames().items():
        if ident != debugger_thread_ident:
            return frame

def _get_current_frame_internal():
    if state.current_thread_type == 'thread':
        return sys._current_frames()[state.current_thread]
    elif state.current_thread_type == 'greenlet':
        gr_id = state.current_thread
        for ob in gc.get_objects():
            if isinstance(ob, sys.modules['greenlet'].greenlet) and id(ob) == gr_id:
                if ob.gr_frame is not None:
                    return ob.gr_frame
                elif ob:
                    # greenlet is active, get it's frame from thread
                    return get_thread_frame()
                else:
                    raise Exception("Greenlet is dead")
                break
        raise Exception("no such greenlet")
    raise Exception("bad current thread type " + state.current_thread_type)

def get_current_frame():
    return apply_frame_offset(_get_current_frame_internal())