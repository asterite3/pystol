import shlex

from attach import attach_to_python_process
import plugins
import args

def main():
    target_pid, interactive, arguments, parser = args.parse_args()

    control_transport, stdio_transport = attach_to_python_process(target_pid)

    if not interactive:
        plugins.plugins[arguments.plugin].run(
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
        plugins.plugins[command_args.plugin].run(
            control_transport,
            stdio_transport,
            command_args
        )

if __name__ == '__main__':
    main()