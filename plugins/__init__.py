import os
import importlib

plugins = {}

for f in os.listdir(os.path.dirname(__file__)):
    if f.startswith('__') or f.endswith('.pyc'):
        continue
    if f.endswith('.py'):
        f = f[:-3]
    plugins[f] = importlib.import_module('.' + f, 'plugins')

def init_args(subparsers):
    for plugin_name in plugins:
        plugin_args_parser = subparsers.add_parser(plugin_name)
        plugin = plugins[plugin_name]
        if hasattr(plugin, 'init_args'):
            plugin.init_args(plugin_args_parser)