import sys

def run(control_transport, stdio_transport, _):
    control_transport.send('import code;code.interact()')
    stdio_transport.in_transport.pipe_from(sys.stdin, 1)
    stdio_transport.in_transport.thread.join()