import os
import sys

with open(os.path.join(os.path.dirname(__file__), 'debugger.py')) as code_file:
    code = code_file.read()

def run(control_transport, stdio_transport, arguments):
    print('kek')
    control_transport.send(code + '\nrun_debugger()')
    stdio_transport.in_transport.pipe_from(sys.stdin, 1)
    stdio_transport.in_transport.thread.join()
