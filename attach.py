import os
import sys

from pydevd_attach_to_process.add_code_to_python_process import run_python_code as run_python_code_in_process

from transport import BidirectionalPipeTransport

INJECTABLES = (
    'real_thread_methods.py',
    'local_proxy.py',
    'stdio_wrapper.py'
)

pad = lambda s: '\n'.join('    ' + l for l in s.splitlines())

def attach_to_python_process(pid):
    stdio_transport = BidirectionalPipeTransport()
    control_transport = BidirectionalPipeTransport()

    code_parts = ['def __pystol_init_code():']

    for injectable in INJECTABLES:
        with open(os.path.join('injectables', injectable)) as injectable_file:
            code_parts.append(pad(injectable_file.read()))

    with open('injectables/debugger_thread_template.py') as template_file:
        template = template_file.read()
        
        code_parts.append(pad(template % (
            stdio_transport.in_transport.path,
            stdio_transport.out_transport.path,
            control_transport.in_transport.path,
            control_transport.out_transport.path
        )))

    code_parts.append('__pystol_init_code();del __pystol_init_code')

    code = '\n'.join(code_parts).replace('\n', '\\n').replace('"', '\\"')

    run_python_code_in_process(pid, code)

    stdio_transport.open_files()
    control_transport.open_files()

    stdio_transport.out_transport.pipe_to(sys.stdout, 1)

    control_transport.send('ping')
    pong = control_transport.recv()
    
    assert pong == 'pong', "Failed to establish control connection, got: " + pong

    control_transport.delete_files()
    stdio_transport.delete_files()

    return control_transport, stdio_transport