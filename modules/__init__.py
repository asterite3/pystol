import os
import importlib

modules = {}

for f in os.listdir(os.path.dirname(__file__)):
    if f.startswith('__') or f.endswith('.pyc'):
        continue
    if f.endswith('.py'):
        f = f[:-3]
    modules[f] = importlib.import_module('.' + f, 'modules')

def init_args(subparsers):
    for plugin_name in modules:
        plugin_args_parser = subparsers.add_parser(plugin_name)
        plugin = modules[plugin_name]
        if hasattr(plugin, 'init_args'):
            plugin.init_args(plugin_args_parser)