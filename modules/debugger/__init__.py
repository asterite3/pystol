import os
import sys
import pprint

from args.interactive_argument_parser import set_interactive

with open(os.path.join(os.path.dirname(__file__), 'sync.py')) as code_file:
    code = code_file.read() + '\n'

with open(os.path.join(os.path.dirname(__file__), 'debugger.py')) as code_file:
    code += code_file.read()

with open(os.path.join(os.path.dirname(__file__), 'current_frame.py')) as code_file:
    current_frame_code = code_file.read()

with open(os.path.join(os.path.dirname(__file__), 'get_closure.py')) as code_file:
    get_closure_code = code_file.read()

def set_thread(control_transport, stdio_transport, arguments):
    thread_id = arguments.thread_id
    control_transport.send('''
import sys
if %d == debugger_thread_ident:
    respond("debugger thread")
elif %d not in sys._current_frames():
    respond("no such thread")
else:
    state.current_thread = %d
    state.current_thread_type = "thread"
    state.frame_offset = 0
    respond("ok")
''' % (thread_id, thread_id, thread_id))
    resp = control_transport.recv()
    assert resp in ('ok', 'no such thread', 'debugger thread')
    if resp == 'no such thread':
        print("No such thread")
    if resp == 'debugger thread':
        print("This is a debugger thread")

def set_greenlet(control_transport, stdio_transport, arguments):
    greenlet_id = arguments.greenlet_id
    control_transport.send('''
import sys
if 'greenlet' not in sys.modules:
    respond("no greenlet module")
else:
    state.current_thread = %d
    state.current_thread_type = "greenlet"
    state.frame_offset = 0
    respond("ok")
''' % greenlet_id)
    resp = control_transport.recv()
    assert resp in ('ok', 'no greenlet module')
    if resp == 'no greenlet module':
        print("Greenlets not available")

def backtrace(control_transport, stdio_transport, arguments):
    with open(os.path.join(os.path.dirname(__file__), 'backtrace.py')) as bt_file:
        control_transport.send(current_frame_code + '\n' + bt_file.read())
    resp = control_transport.recv()

    if isinstance(resp, list):
        print(''.join(resp))
    else:
        print('error: ' + resp)

def get_locals(control_transport, stdio_transport, arguments):
    control_transport.send(current_frame_code + '''
import traceback
try:
    respond({k: repr(v) for k, v in get_current_frame().f_locals.items()})
except:
    respond(traceback.format_exc())
''')
    resp = control_transport.recv()
    if isinstance(resp, dict):
        for k, v in resp.items():
            print('%s = %s' % (k, v))
    else:
        print('error: ' + resp)

def get_globals(control_transport, stdio_transport, arguments):
    control_transport.send(current_frame_code + '''
import traceback
try:
    respond({k: repr(v) for k, v in get_current_frame().f_globals.items()})
except:
    respond(traceback.format_exc())
''')
    resp = control_transport.recv()
    if isinstance(resp, dict):
        for k, v in resp.items():
            print('%s = %s' % (k, v))
    else:
        print('error: ' + resp)

def get_closure_vars(control_transport, stdio_transport, arguments):
    control_transport.send(current_frame_code + '\n' + get_closure_code + '''
import traceback
try:
    respond({k: repr(v) for k, v in get_closure(get_current_frame()).items()})
except:
    respond(traceback.format_exc())
''')
    resp = control_transport.recv()
    if isinstance(resp, dict):
        for k, v in resp.items():
            print('%s = %s' % (k, v))
    else:
        print('error: ' + resp)

def examine(control_transport, stdio_transport, arguments):
    name = arguments.var_name
    control_transport.send(current_frame_code + '\n' + get_closure_code + '''
import traceback
try:
    name = %s
    frame = get_current_frame()
    if name in frame.f_locals:
        respond(repr(frame.f_locals[name]))
    elif name in frame.f_globals:
        respond(repr(frame.f_globals[name]))
    else:
        closure = get_closure(frame)
        if name in closure:
            respond(repr(closure[name]))
        else:
            respond({"status": "fail", "error": "variable not found"})
except:
    respond({"status": "fail", "error": traceback.format_exc()})
''' % (repr(name)))
    resp = control_transport.recv()
    if isinstance(resp, dict):
        print('error: ' + resp['error'])
    else:
        print(resp)

def up(control_transport, _, arguments):
    count = arguments.count
    control_transport.send(
        'state.frame_offset = max(0, getattr(state, "frame_offset", 0) + %d); respond("ok")' % count
    )
    assert control_transport.recv() == "ok"

def down(control_transport, _, arguments):
    count = arguments.count
    control_transport.send(
        'state.frame_offset = max(0, getattr(state, "frame_offset", 0) - %d); respond("ok")' % count
    )
    assert control_transport.recv() == "ok"

def run(control_transport, stdio_transport, arguments):
    control_transport.send(code + '\nrun_debugger()')
    stdio_transport.in_transport.pipe_from(sys.stdin, 1)
    stdio_transport.in_transport.thread.join()

def init_args_raw(subparsers, commands, interactive):
    if not interactive:
        return
    set_thread_parser = subparsers.add_parser('thread')
    commands['thread'] = set_thread
    set_thread_parser.add_argument('thread_id', type=int)
    set_interactive(set_thread_parser)

    set_greenlet_parser = subparsers.add_parser('greenlet')
    commands['greenlet'] = set_greenlet
    set_greenlet_parser.add_argument('greenlet_id', type=int)
    set_interactive(set_greenlet_parser)

    locals_parser = subparsers.add_parser('locals')
    commands['locals'] = get_locals
    set_interactive(locals_parser)

    globals_parser = subparsers.add_parser('globals')
    commands['globals'] = get_globals
    set_interactive(globals_parser)

    closure_parser = subparsers.add_parser('closure')
    commands['closure'] = get_closure_vars
    set_interactive(closure_parser)

    for alias in ('backtrace', 'bt'):
        backtrace_parser = subparsers.add_parser(alias)
        commands[alias] = backtrace
        set_interactive(backtrace_parser)

    for alias in ('x', 'examine', 'print', 'p'):
        examine_parser = subparsers.add_parser(alias)
        examine_parser.add_argument('var_name')
        commands[alias] = examine
        set_interactive(examine_parser)

    up_parser = subparsers.add_parser('up')
    up_parser.add_argument('-c', '--count', type=int, default=1, required=False)
    commands['up'] = up
    set_interactive(up_parser)

    down_parser = subparsers.add_parser('down')
    down_parser.add_argument('-c', '--count', type=int, default=1, required=False)
    commands['down'] = down
    set_interactive(down_parser)

    commands['debugger'] = run