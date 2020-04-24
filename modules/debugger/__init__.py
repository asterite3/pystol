import os
import sys

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

def run(control_transport, stdio_transport, arguments):
    control_transport.send(code + '\nrun_debugger()')
    stdio_transport.in_transport.pipe_from(sys.stdin, 1)
    stdio_transport.in_transport.thread.join()

def init_args_raw(subparsers, commands):
    set_thread_parser = subparsers.add_parser('thread')
    commands['thread'] = set_thread
    set_thread_parser.add_argument('thread_id', type=int)
    set_thread_parser.pystol_no_exit = True
    set_thread_parser.prog = 'pystol>'

    commands['debugger'] = run