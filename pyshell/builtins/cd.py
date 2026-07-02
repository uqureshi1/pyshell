import os

from pyshell.execution.redirection import output_error_to_target
from pyshell.registry import registry


@registry.register("cd")
def run(args, ctx):
    new_dir = args[0] if args else "~"
    if new_dir == "~":
        new_dir = os.path.expanduser("~")

    if os.path.isdir(new_dir):
        os.chdir(new_dir)
        return 0

    output_error_to_target(f"cd: {new_dir}: No such file or directory", args)
    return 1
