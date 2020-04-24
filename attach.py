import os
import sys
import tempfile

from pydevd_attach_to_process.add_code_to_python_process import run_python_code as run_python_code_in_process

from transport import BidirectionalPipeTransport
from leftpad import leftpad

INJECTABLES = (
    'real_thread_methods.py',
    'local_proxy.py',
    'stdio_wrapper.py',
    'state.py',
    'debugger_thread.py'
)

def _attach_to_python_process_with_transport(pid, stdio_transport, control_transport):
    code_parts = ['def __pystol_init_code():']

    for injectable in INJECTABLES:
        with open(os.path.join('injectables', injectable)) as injectable_file:
            code_parts.append(leftpad(injectable_file.read()))

    code_parts.append('__pystol_init_code();del __pystol_init_code')

    with tempfile.NamedTemporaryFile(prefix='pystolinit', suffix='.py') as init_code_file:
        code = '\n'.join(code_parts)

        if str is not bytes:
            code = bytes(code, 'utf8')

        init_code_file.write(code)

        run_python_code_in_process(pid, ('''
            exec(open("%s").read(), {
            "pystol_stdin": "%s",
            "pystol_stdout": "%s",
            "pystol_control_in": "%s",
            "pystol_control_out": "%s"
        })''' % (
            init_code_file.name,
            stdio_transport.in_transport.path,
            stdio_transport.out_transport.path,
            control_transport.in_transport.path,
            control_transport.out_transport.path
        )).replace('\n', '').replace(' ', '').replace('"', '\\"'))

        stdio_transport.open_files()
        control_transport.open_files()

        stdio_transport.out_transport.pipe_to(sys.stdout, 1)

        control_transport.send('ping')
        pong = control_transport.recv()

        assert pong == 'pong', "Failed to establish control connection, got: " + pong

def attach_to_python_process(pid):
    stdio_transport = BidirectionalPipeTransport()
    control_transport = BidirectionalPipeTransport()

    try:
        _attach_to_python_process_with_transport(pid, stdio_transport, control_transport)
    finally:
        control_transport.delete_files()
        stdio_transport.delete_files()

    return control_transport, stdio_transport