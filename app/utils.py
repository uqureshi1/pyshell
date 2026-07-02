import sys

from .constants import REDIRECTION_OPERATORS, StdoutTarget, StdStreams


def _redirection_indices(arguments):
    return [i for i, arg in enumerate(arguments) if arg in REDIRECTION_OPERATORS]


def get_output_stream(redirection_operator):
    if redirection_operator in [">", "1>", ">>", "1>>"]:
        return StdStreams.STDOUT
    elif redirection_operator in ["2>", "2>>"]:
        return StdStreams.STDERR
    else:
        raise ValueError(f"Invalid redirection operator: {redirection_operator}")


def get_output_mode(arguments):
    indices = _redirection_indices(arguments)
    if len(indices) > 1:
        print("Syntax error: multiple redirection operators", file=sys.stderr)
        return None, None, None, None

    if len(indices) == 1:
        redirection_index = indices[0]
        if redirection_index == len(arguments) - 1:
            print("Syntax error: no file specified for redirection", file=sys.stderr)
            return None, None, None, None

        output_file = arguments[redirection_index + 1]
        return (
            StdoutTarget.FILE,
            output_file,
            get_output_stream(arguments[redirection_index]),
            get_file_mode(arguments[redirection_index]),
        )

    return StdoutTarget.STDOUT, None, None, None


def strip_redirection(arguments):
    indices = _redirection_indices(arguments)
    if len(indices) == 1:
        return arguments[: indices[0]]
    return arguments


def get_file_mode(redirection_operator):
    if redirection_operator in [">", "1>", "2>"]:
        return "w"
    elif redirection_operator in [">>", "1>>", "2>>"]:
        return "a"
    else:
        raise ValueError(f"Invalid redirection operator: {redirection_operator}")


def output_to_target(
    output,
    target=StdoutTarget.STDOUT,
    output_file=None,
    stream=StdStreams.STDOUT,
    file_mode="w",
    content_stream=StdStreams.STDOUT,
):
    if target == StdoutTarget.FILE and stream == content_stream:
        with open(output_file, file_mode) as f:
            f.write(output + "\n")
    else:
        print(
            output,
            file=sys.stderr if content_stream == StdStreams.STDERR else sys.stdout,
        )
        if target == StdoutTarget.FILE:
            open(output_file, file_mode).close()


def has_redirection(arguments):
    return len(_redirection_indices(arguments)) == 1
