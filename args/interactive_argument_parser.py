import sys
import argparse

class ArgumentParseError(Exception):
    pass

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        if hasattr(self, 'pystol_no_exit'):
            self.print_usage(sys.stderr)
            raise ArgumentParseError
        super(ArgumentParser, self).error(message)

def set_interactive(parser):
    parser._handle_conflict_resolve(None, [('--help',parser._actions[0])])
    parser._handle_conflict_resolve(None, [('-h',parser._actions[0])])
    prog_parts = parser.prog.split()
    if len(prog_parts) > 0:
        prog_parts[0] = 'pystol>'
    else:
        prog_parts = ['pystol>']
    parser.prog = ' '.join(prog_parts)
    parser.pystol_no_exit = True