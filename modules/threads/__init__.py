import os

from leftpad import leftpad

with open(os.path.join(os.path.dirname(__file__), 'dump_threads.py')) as code_file:
    code = code_file.read()

def init_args(parser):
    parser.add_argument('--stacks', action='store_true', default=False)

def run(control_transport, _, arguments):
    control_transport.send(
        code + '\nrespond(dump_threads(' + str(arguments.stacks) + '))'
    )
    response = control_transport.recv()

    threads = response['threads']

    print("%d threads:" % len(threads))

    for thread in threads:
        tag = ''
        if thread['is_debugger']:
            tag = ' [DEBUGGER THREAD]'
        marker = '   '
        if thread['current']:
            marker = ' * '
        print('%s%d %s%s' % (marker, thread['ident'], thread['name'], tag))
        if arguments.stacks:
            print(leftpad(''.join(thread['stack']), 3))

    if 'greenlets' in response:
        greenlets = response['greenlets']
        print("\n%d greenlets:" % len(greenlets))
        for g in greenlets:
            marker = '   '
            if g['current']:
                marker = ' * '
            print(marker + str(g['id']) + ' ' + g['name'])
            if arguments.stacks:
                print(leftpad(''.join(g['stack']), 3))