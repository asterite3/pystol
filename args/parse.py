import sys
import string

import modules

from .interactive_argument_parser import ArgumentParser, set_interactive

isnumber = lambda s: all(c in string.digits for c in s)

def parse_args():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='module')

    target_pid = None
    arguments = None

    args = sys.argv[1:]
    interactive = True

    if len(args) >= 1 and isnumber(args[0]):
        target_pid = int(args[0])
        args = args[1:]
    elif len(args) >= 2 and args[0] == '-p' and isnumber(args[1]):
        target_pid = int(args[1])
        args = args[2:]
    if len(args) > 0 or target_pid is None:
        interactive = False

    if target_pid is None:
        parser.add_argument('-p', '--pid', type=int, required=True)

    modules.init_args(subparsers, interactive)

    if not interactive:
        arguments = parser.parse_args(args)
        if target_pid is None:
            target_pid = arguments.pid

    if interactive:
        set_interactive(parser)
        parser.prog = 'pystol>'

    return target_pid, interactive, arguments, parser