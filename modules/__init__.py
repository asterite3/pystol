import os
import importlib

modules = {}
commands = {}

for f in os.listdir(os.path.dirname(__file__)):
    if f.startswith('__') or f.endswith('.pyc'):
        continue
    if f.endswith('.py'):
        f = f[:-3]
    modules[f] = importlib.import_module('.' + f, 'modules')

def init_args(subparsers, interactive):
    for plugin_name in modules:
        plugin = modules[plugin_name]
        if hasattr(plugin, 'init_args_raw'):
            plugin.init_args_raw(subparsers, commands, interactive)
            continue
        commands[plugin_name] = plugin.run
        plugin_args_parser = subparsers.add_parser(plugin_name)
        if hasattr(plugin, 'init_args'):
            plugin.init_args(plugin_args_parser)