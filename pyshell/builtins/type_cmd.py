from pyshell.execution.executor import resolve_executable
from pyshell.execution.redirection import get_output_mode, output_error_to_target, output_to_target
from pyshell.registry import registry


@registry.register("type")
def run(args, ctx):
    if not args:
        output_error_to_target("type: usage: type name", args)
        return 1

    command_to_check = args[0]
    if registry.is_builtin(command_to_check):
        output_to_target(f"{command_to_check} is a shell builtin", *get_output_mode(args))
        return 0

    full_path = resolve_executable(command_to_check)
    if full_path is not None:
        output_to_target(f"{command_to_check} is {full_path}", *get_output_mode(args))
        return 0

    output_error_to_target(f"{command_to_check}: not found", args)
    return 1
