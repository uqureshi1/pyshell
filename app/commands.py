import os
import readline
import subprocess
import sys

from .constants import HANDLED_COMMANDS, StdoutTarget, StdStreams
from .utils import get_output_mode, output_to_target, strip_redirection

REGISTERED_COMPLETES = {}
BACKGROUND_JOBS = []
DECLARED_VARIABLES = {}
_HISTORY_APPEND_OFFSET = 0


def present_working_directory(arguments):
    output_to_target(os.getcwd(), *get_output_mode(arguments))


def change_directory(arguments):
    new_dir = arguments[0]
    if new_dir == "~":
        new_dir = os.path.expanduser("~")
    if os.path.isdir(new_dir):
        os.chdir(new_dir)
    else:
        output_to_target(f"cd: {new_dir}: No such file or directory", *get_output_mode(arguments))


def type_command(arguments):
    command_to_check = arguments[0]
    if command_to_check in HANDLED_COMMANDS:
        output_to_target(f"{command_to_check} is a shell builtin", *get_output_mode(arguments))
    else:
        found = False
        for path in os.environ["PATH"].split(os.pathsep):
            full_path = os.path.join(path, command_to_check)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                output_to_target(f"{command_to_check} is {full_path}", *get_output_mode(arguments))
                found = True
                break
        if not found:
            output_to_target(f"{command_to_check} not found", *get_output_mode(arguments))


def echo_command(arguments):
    output_args = strip_redirection(arguments)
    output_to_target(" ".join(output_args), *get_output_mode(arguments))


def handle_external_command(command, arguments):
    found = False
    is_background = False
    if len(arguments) >= 1 and arguments[-1] == "&":
        is_background = True
        arguments = arguments[:-1]

    if command not in HANDLED_COMMANDS:
        for path in os.environ["PATH"].split(os.pathsep):
            full_path = os.path.join(path, command)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                args = {}
                target, output_file, stream, file_mode = get_output_mode(arguments)
                mode = open(output_file, file_mode) if target == StdoutTarget.FILE else None
                if stream == StdStreams.STDOUT:
                    args["stdout"] = mode or subprocess.PIPE
                else:
                    args["stderr"] = mode or subprocess.PIPE
                try:
                    if is_background:
                        process = subprocess.Popen(
                            [command] + list(strip_redirection(arguments)),
                            executable=full_path,
                            **args,
                        )
                        BACKGROUND_JOBS.append(
                            {
                                "id": len(BACKGROUND_JOBS) + 1,
                                "process": process,
                                "command": " ".join([command] + list(arguments)),
                            }
                        )
                        output_to_target(f"[{len(BACKGROUND_JOBS)}] {process.pid}")
                    else:
                        subprocess.run(
                            [command] + list(strip_redirection(arguments)),
                            executable=full_path,
                            **args,
                        )
                finally:
                    if mode:
                        mode.close()
                found = True
                break

    if not found:
        output_to_target(f"{command}: command not found", *get_output_mode(arguments))


def _resolve_executable(command):
    for path in os.environ["PATH"].split(os.pathsep):
        candidate = os.path.join(path, command)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def _run_builtin_pipeline_stage(command, arguments, stdout_fd):
    from .dispatcher import command_dispatcher

    if stdout_fd is None:
        command_dispatcher(command, arguments)
        return

    write_file = os.fdopen(stdout_fd, "w")
    old_stdout = sys.stdout
    sys.stdout = write_file
    try:
        command_dispatcher(command, arguments)
    finally:
        sys.stdout = old_stdout
        write_file.close()


def handle_pipeline_command(segments):
    stage_count = len(segments)
    pipe_fds = [os.pipe() for _ in range(stage_count - 1)]
    processes = []

    for index, (command, arguments) in enumerate(segments):
        is_last = index == stage_count - 1
        stdin_fd = pipe_fds[index - 1][0] if index > 0 else None
        stdout_fd = pipe_fds[index][1] if not is_last else None

        if command in HANDLED_COMMANDS:
            _run_builtin_pipeline_stage(command, arguments, stdout_fd)
            if stdin_fd is not None:
                os.close(stdin_fd)
            continue

        full_path = _resolve_executable(command)
        if full_path is None:
            output_to_target(f"{command}: command not found", *get_output_mode(arguments))
            if stdin_fd is not None:
                os.close(stdin_fd)
            if stdout_fd is not None:
                os.close(stdout_fd)
            continue

        out_file = None
        popen_stdout = stdout_fd
        if is_last:
            target, output_file, stream, file_mode = get_output_mode(arguments)
            if target == StdoutTarget.FILE and stream == StdStreams.STDOUT:
                out_file = open(output_file, file_mode)
                popen_stdout = out_file

        process = subprocess.Popen(
            [command] + list(strip_redirection(arguments)),
            executable=full_path,
            stdin=stdin_fd,
            stdout=popen_stdout,
        )
        processes.append(process)

        if stdin_fd is not None:
            os.close(stdin_fd)
        if stdout_fd is not None:
            os.close(stdout_fd)
        if out_file is not None:
            out_file.close()

    for process in processes:
        process.wait()


def exit_command():
    sys.exit(0)


def handle_complete_command(arguments):
    command = arguments[-1]
    if len(arguments) == 2 and arguments[0] == "-p":
        if command in REGISTERED_COMPLETES:
            completion = REGISTERED_COMPLETES[command]
            output_to_target(f"complete -C '{completion}' {command}", *get_output_mode(arguments))
        else:
            output_to_target(
                f"complete: {arguments[1]}: no completion specification",
                *get_output_mode(arguments),
            )
    elif len(arguments) == 3 and arguments[0] == "-C":
        REGISTERED_COMPLETES[arguments[2]] = arguments[1]
    elif len(arguments) == 2 and arguments[0] == "-r":
        REGISTERED_COMPLETES.pop(arguments[1], None)


def handle_jobs_command(completed_only=False):
    last_index = len(BACKGROUND_JOBS) - 1
    indexes_to_remove = []
    for index, job in enumerate(BACKGROUND_JOBS):
        marker = " "
        if index == last_index:
            marker = "+"
        elif index == last_index - 1:
            marker = "-"
        status = "Running" if job["process"].poll() is None else "Done"

        if status == "Running" and completed_only:
            continue

        suffix = " &" if status == "Running" else ""
        output_to_target(f"[{job['id']}]{marker}  {status:<24}{job['command']}{suffix}")
        if status == "Done":
            indexes_to_remove.append(index)

    for idx in indexes_to_remove:
        BACKGROUND_JOBS.pop(idx)


def handle_history_command(arguments):
    if arguments and arguments[0] == "-r" and len(arguments) == 2:
        file_path = arguments[1]
        if os.path.isfile(file_path):
            with open(file_path) as f:
                for line in f:
                    line = line.rstrip("\n")
                    if line:
                        readline.add_history(line)
        return

    if arguments and arguments[0] in ["-w", "-a"] and len(arguments) == 2:
        global _HISTORY_APPEND_OFFSET
        file_path = arguments[1]
        length = readline.get_current_history_length()
        is_append = arguments[0] == "-a"
        start = _HISTORY_APPEND_OFFSET + 1 if is_append else 1
        with open(file_path, "a" if is_append else "w") as f:
            for i in range(start, length + 1):
                f.write(readline.get_history_item(i) + "\n")
        _HISTORY_APPEND_OFFSET = length
        return

    length = readline.get_current_history_length()
    start = 1
    if arguments:
        try:
            limit = int(arguments[-1])
            start = max(1, length - limit + 1)
        except ValueError:
            pass

    for i in range(start, length + 1):
        print(f"{i:5}  {readline.get_history_item(i)}")


def handle_declare_command(arguments):
    if len(arguments) == 2 and arguments[0] == "-p":
        if arguments[1] not in DECLARED_VARIABLES:
            output_to_target(f"declare: {arguments[1]}: not found", *get_output_mode(arguments))
        else:
            output_to_target(
                f"declare -- {arguments[1]}" + "=" + f'"{DECLARED_VARIABLES[arguments[1]]}"',
                *get_output_mode(arguments),
            )

    elif len(arguments) == 1 and "=" in arguments[0]:
        key, value = arguments[0].split("=", 1)
        if not _is_valid_identifier(key):
            output_to_target(
                f"declare: `{arguments[0]}': not a valid identifier",
                *get_output_mode(arguments),
            )
        else:
            DECLARED_VARIABLES[key] = value


def _is_valid_identifier(name):
    if not name:
        return False
    if not (name[0].isalpha() or name[0] == "_"):
        return False
    return all(c.isalnum() or c == "_" for c in name[1:])
