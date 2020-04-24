import sys
import traceback
import threading
import gc
import traceback

def dump_greenlets(dump_stacks, response, non_debugger_thread):
    from greenlet import greenlet

    greenlets = []
    response['greenlets'] = []

    for ob in gc.get_objects():
        if not isinstance(ob, greenlet):
            continue
        if not ob:
            continue
        greenlets.append(ob)
    for g in greenlets:
        current = (
            getattr(state, 'current_thread_type', '') == 'greenlet' and
            getattr(state, 'current_thread', None) == id(g)
        )
        greenlet_info = {
            'name': str(g),
            'id': id(g),
            'current': current
        }
        if dump_stacks:
            frame = g.gr_frame
            if frame is not None:
                greenlet_info['stack'] = traceback.format_stack(frame, 500)
            elif g:
                greenlet_info['stack'] = traceback.format_stack(sys._current_frames()[non_debugger_thread], 500)
            else:
                greenlet_info['stack'] = ['GREENLET IS DEAD\n']
        response['greenlets'].append(greenlet_info)
    try:
        del ob
        del g
    except NameError:
        pass

def dump_threads(dump_stacks):
    threads = sys._current_frames()

    response = {
        'threads': []
    }

    non_debugger_thread = None

    for ident, stack in threads.items():
        name = ''
        if ident in threading._active:
            name = threading._active[ident].name
        current = (
            getattr(state, 'current_thread_type', '') == 'thread' and
            getattr(state, 'current_thread', None) == ident
        )

        is_debugger = ident == debugger_thread_ident
        non_debugger_thread = ident

        thread_info = {
            'ident': ident,
            'name': name,
            'is_debugger': is_debugger,
            'current': current
        }
        if dump_stacks:
            thread_info['stack'] = traceback.format_stack(stack)
        response['threads'].append(thread_info)

    if 'greenlet' in sys.modules:
        dump_greenlets(dump_stacks, response, non_debugger_thread)
    return response