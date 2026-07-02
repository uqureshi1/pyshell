import os

from pyshell.execution.redirection import get_output_mode, output_to_target
from pyshell.registry import registry


@registry.register("pwd")
def run(args, ctx):
    output_to_target(os.getcwd(), *get_output_mode(args))
    return 0
