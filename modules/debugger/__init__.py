import os
import sys

from args.interactive_argument_parser import set_interactive

with open(os.path.join(os.path.dirname(__file__), 'sync.py')) as code_file:
    code = code_file.read() + '\n'

with open(os.path.join(os.path.dirname(__file__), 'debugger.py')) as code_file:
    code += code_file.read()

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
    respond("ok")
''' % greenlet_id)
    resp = control_transport.recv()
    assert resp in ('ok', 'no greenlet module')
    if resp == 'no greenlet module':
        print("Greenlets not available")

def run(control_transport, stdio_transport, arguments):
    control_transport.send(code + '\nrun_debugger()')
    stdio_transport.in_transport.pipe_from(sys.stdin, 1)
    stdio_transport.in_transport.thread.join()

def init_args_raw(subparsers, commands):
    set_thread_parser = subparsers.add_parser('thread')
    commands['thread'] = set_thread
    set_thread_parser.add_argument('thread_id', type=int)
    set_interactive(set_thread_parser)

    set_greenlet_parser = subparsers.add_parser('greenlet')
    commands['greenlet'] = set_greenlet
    set_greenlet_parser.add_argument('greenlet_id', type=int)
    set_interactive(set_greenlet_parser)

    commands['debugger'] = run