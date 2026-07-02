from pyshell.execution.redirection import get_output_mode, output_to_target, strip_redirection
from pyshell.registry import registry


@registry.register("echo")
def run(args, ctx):
    output_args = strip_redirection(args)
    output_to_target(" ".join(output_args), *get_output_mode(args))
    return 0
