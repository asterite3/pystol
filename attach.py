import sys

from pydevd_attach_to_process.add_code_to_python_process import run_python_code as run_python_code_in_process

from transport import BidirectionalPipeTransport

def attach_to_python_process(pid):
    stdio_transport = BidirectionalPipeTransport()
    control_transport = BidirectionalPipeTransport()

    code_parts = []

    with open('injectables/real_thread_methods.py') as real_thread_methods_file:
        code_parts.append(real_thread_methods_file.read())

    with open('injectables/local_proxy.py') as local_proxy_file:
        code_parts.append(local_proxy_file.read())

    with open('injectables/stdio_wrapper.py') as stdio_wrapper_file:
        code_parts.append(stdio_wrapper_file.read())

    with open('injectables/debugger_thread_template.py') as template_file:
        template = template_file.read()
        
        code_parts.append(template % (
            stdio_transport.in_transport.path,
            stdio_transport.out_transport.path,
            control_transport.in_transport.path,
            control_transport.out_transport.path
        ))

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