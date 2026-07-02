import os
import subprocess
import sys

from pyshell.constants import StdoutTarget, StdStreams
from pyshell.execution.redirection import (
    get_output_mode,
    output_error_to_target,
    strip_redirection,
)
from pyshell.registry import registry


def _candidate_suffixes():
    """Suffixes to try when resolving a bare command name against PATH."""
    if os.name != "nt":
        return [""]
    pathext = os.environ.get("PATHEXT", ".COM;.EXE;.BAT;.CMD")
    return ["", *[ext for ext in pathext.split(os.pathsep) if ext]]


def resolve_executable(command):
    for path in os.environ.get("PATH", "").split(os.pathsep):
        for suffix in _candidate_suffixes():
            candidate = os.path.join(path, command + suffix)
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
    return None


def dispatch(command, arguments, ctx):
    handler = registry.get(command)
    if handler is not None:
        ctx.exit_status = handler(arguments, ctx) or 0
    else:
        ctx.exit_status = run_external(command, arguments, ctx)


def run_external(command, arguments, ctx):
    is_background = bool(arguments) and arguments[-1] == "&"
    if is_background:
        arguments = arguments[:-1]

    full_path = resolve_executable(command)
    if full_path is None:
        output_error_to_target(f"{command}: command not found", arguments)
        return 127

    target, output_file, stream, file_mode = get_output_mode(arguments)
    handle = open(output_file, file_mode) if target == StdoutTarget.FILE else None

    popen_kwargs = {}
    if handle is not None:
        popen_kwargs["stdout" if stream == StdStreams.STDOUT else "stderr"] = handle

    try:
        if is_background:
            process = subprocess.Popen(
                [command, *strip_redirection(arguments)],
                executable=full_path,
                **popen_kwargs,
            )
            job = ctx.jobs.add(process, " ".join([command, *arguments]))
            print(f"[{job['id']}] {process.pid}")
            return 0

        result = subprocess.run(
            [command, *strip_redirection(arguments)],
            executable=full_path,
            **popen_kwargs,
        )
        return result.returncode
    finally:
        if handle:
            handle.close()


def _run_builtin_pipeline_stage(command, arguments, stdout_fd, ctx):
    if stdout_fd is None:
        dispatch(command, arguments, ctx)
        return

    write_file = os.fdopen(stdout_fd, "w")
    old_stdout = sys.stdout
    sys.stdout = write_file
    try:
        dispatch(command, arguments, ctx)
    finally:
        sys.stdout = old_stdout
        write_file.close()


def run_pipeline(segments, ctx):
    stage_count = len(segments)
    pipe_fds = [os.pipe() for _ in range(stage_count - 1)]
    processes = []

    for index, (command, arguments) in enumerate(segments):
        is_last = index == stage_count - 1
        stdin_fd = pipe_fds[index - 1][0] if index > 0 else None
        stdout_fd = pipe_fds[index][1] if not is_last else None

        if registry.is_builtin(command):
            _run_builtin_pipeline_stage(command, arguments, stdout_fd, ctx)
            if stdin_fd is not None:
                os.close(stdin_fd)
            continue

        full_path = resolve_executable(command)
        if full_path is None:
            output_error_to_target(f"{command}: command not found", arguments)
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
            [command, *strip_redirection(arguments)],
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
    ctx.exit_status = processes[-1].returncode if processes else 0
