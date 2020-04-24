import gc, sys, traceback

def backtrace():
    try:
        if state.current_thread_type == 'thread':
            return traceback.format_stack(sys._current_frames()[state.current_thread])
        elif state.current_thread_type == 'greenlet':
            gr_id = state.current_thread
            if state.saved_greenlet_stack is not None and id(state.saved_greenlet_stack['greenlet']) == gr_id:
                return state.saved_greenlet_stack['stack']
            for ob in gc.get_objects():
                if isinstance(ob, sys.modules['greenlet'].greenlet) and id(ob) == gr_id:
                    if ob.gr_frame is not None:
                        return traceback.format_stack(ob.gr_frame)
                    else:
                        return 'stack frame not available'
                    break
            return 'no such greenlet'
        return 'bad current thread type ' + state.current_thread_type
    except:
        traceback.print_exc()
        respond('printing traceback failed')
        raise

respond(backtrace())