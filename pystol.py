import shlex

from attach import attach_to_python_process
import modules
import args

def main():
    global raw_input

    target_pid, interactive, arguments, parser = args.parse_args()

    control_transport, stdio_transport = attach_to_python_process(target_pid)

    if not interactive:
        modules.commands[arguments.module](
            control_transport,
            stdio_transport,
            arguments
        )
        return
    try:
        raw_input
    except NameError:
        raw_input = input
    while True:
        try:
            command = raw_input('pystol> ')
        except EOFError:
            break
        if command == '':
            continue
        try:
            command_args = parser.parse_args(shlex.split(command))
        except args.ArgumentParseError:
            continue
        modules.commands[command_args.module](
            control_transport,
            stdio_transport,
            command_args
        )

if __name__ == '__main__':
    main()