import sys

from attach import attach_to_python_process

control_transport, stdio_transport = attach_to_python_process(int(sys.argv[1]))

control_transport.send('''
import code
respond('ok')
code.interact()
''')

print(control_transport.recv())
stdio_transport.in_transport.pipe_from(sys.stdin, 1)

stdio_transport.in_transport.thread.join()