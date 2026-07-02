from pyshell.execution.redirection import get_output_mode, output_error_to_target, output_to_target
from pyshell.registry import registry


@registry.register("declare")
def run(args, ctx):
    if len(args) == 2 and args[0] == "-p":
        if args[1] not in ctx.declared_vars:
            output_error_to_target(f"declare: {args[1]}: not found", args)
            return 1
        output_to_target(
            f'declare -- {args[1]}="{ctx.declared_vars[args[1]]}"',
            *get_output_mode(args),
        )
        return 0

    if len(args) == 1 and "=" in args[0]:
        key, value = args[0].split("=", 1)
        if not _is_valid_identifier(key):
            output_error_to_target(f"declare: `{args[0]}': not a valid identifier", args)
            return 1
        ctx.declared_vars[key] = value
        return 0

    return 0


def _is_valid_identifier(name):
    if not name:
        return False
    if not (name[0].isalpha() or name[0] == "_"):
        return False
    return all(c.isalnum() or c == "_" for c in name[1:])
