import os
import readline

from pyshell.registry import registry


@registry.register("history")
def run(args, ctx):
    if args and args[0] == "-r" and len(args) == 2:
        _read_history_file(args[1])
        return 0

    if args and args[0] in ("-w", "-a") and len(args) == 2:
        _write_history_file(args[1], append=args[0] == "-a", ctx=ctx)
        return 0

    _print_history(args)
    return 0


def _read_history_file(file_path):
    if not os.path.isfile(file_path):
        return
    with open(file_path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line:
                readline.add_history(line)


def _write_history_file(file_path, append, ctx):
    length = readline.get_current_history_length()
    start = ctx.history_append_offset + 1 if append else 1
    with open(file_path, "a" if append else "w") as f:
        for i in range(start, length + 1):
            f.write(readline.get_history_item(i) + "\n")
    ctx.history_append_offset = length


def _print_history(args):
    length = readline.get_current_history_length()
    start = 1
    if args:
        try:
            limit = int(args[-1])
            start = max(1, length - limit + 1)
        except ValueError:
            pass

    for i in range(start, length + 1):
        print(f"{i:5}  {readline.get_history_item(i)}")
