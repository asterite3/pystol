import sys
import argparse
import string

import plugins

class ArgumentParseError(Exception):
    pass

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        if hasattr(self, 'pystol_no_exit'):
            self.print_usage(sys.stderr)
            raise ArgumentParseError
        super(ArgumentParser, self).error(message)

isnumber = lambda s: all(c in string.digits for c in s)

def parse_args():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='plugin')

    plugins.init_args(subparsers)

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
        if target_pid is None:
            parser.add_argument('-p', '--pid', type=int, required=True)
        arguments = parser.parse_args(args)
        if target_pid is None:
            target_pid = arguments.pid
        interactive = False

    if interactive:
        parser._handle_conflict_resolve(None, [('--help',parser._actions[0])])
        parser._handle_conflict_resolve(None, [('-h',parser._actions[0])])
        parser.prog = 'pystol>'
        parser.pystol_no_exit = True

    return target_pid, interactive, arguments, parser