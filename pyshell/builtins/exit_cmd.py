import sys

from pyshell.registry import registry


@registry.register("exit")
def run(args, ctx):
    code = 0
    if args:
        try:
            code = int(args[0])
        except ValueError:
            code = 0
    sys.exit(code)
