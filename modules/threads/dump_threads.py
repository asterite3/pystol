import sys
import traceback
import threading
import gc
import traceback

def dump_greenlets(dump_stacks, response):
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
        greenlet_info = {
            'name': str(g)
        }
        if dump_stacks:
            frame = g.gr_frame
            if frame is not None:
                greenlet_info['stack'] = traceback.format_stack(frame, 500)
            elif saved_greenlet_stack is not None and g is saved_greenlet_stack['greenlet']:
                greenlet_info['stack'] = saved_greenlet_stack['stack']
            else:
                greenlet_info['stack'] = ['NOT AVAILABLE\n']
        response['greenlets'].append(greenlet_info)
    try:
        del ob
        del g
    except NameError:
        pass

def dump_threads(dump_stacks):
    threads = threading.enumerate()

    response = {
        'threads': []
    }

    if dump_stacks:
        thread_stacks = sys._current_frames()

    debugger_thread_ident = get_ident()
    for thread in threads:
        thread_info = {
            'ident': thread.ident,
            'name': thread.getName(),
            'is_debugger': thread.ident == debugger_thread_ident
        }
        if dump_stacks:
            if thread.ident in thread_stacks:
                thread_info['stack'] = traceback.format_stack(thread_stacks[thread.ident])
            else:
                thread_info['stack'] = ['NOT AVAILABLE\n']
        response['threads'].append(thread_info)

    if 'greenlet' in sys.modules:
        dump_greenlets(dump_stacks, response)
    return response