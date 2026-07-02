from pyshell.execution.redirection import get_output_mode, output_error_to_target, output_to_target
from pyshell.registry import registry


@registry.register("complete")
def run(args, ctx):
    if not args:
        return 0

    if len(args) == 2 and args[0] == "-p":
        command = args[1]
        if command in ctx.completions:
            completion = ctx.completions[command]
            output_to_target(f"complete -C '{completion}' {command}", *get_output_mode(args))
        else:
            output_error_to_target(f"complete: {command}: no completion specification", args)
        return 0

    if len(args) == 3 and args[0] == "-C":
        ctx.completions[args[2]] = args[1]
        return 0

    if len(args) == 2 and args[0] == "-r":
        ctx.completions.pop(args[1], None)
        return 0

    return 0
