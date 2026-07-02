import os
try:
    import readline
except ImportError:
    import pyreadline3 as readline  # Windows fallback
import subprocess
import atexit
from pathlib import Path

from .tokenizer import tokenize, split_pipeline
from .dispatcher import command_dispatcher
from .constants import AUTO_COMPLETE_COMMANDS
from .commands import REGISTERED_COMPLETES, handle_jobs_command, handle_pipeline_command


def configure_history():
    if hasattr(readline, "set_auto_history"):
        readline.set_auto_history(False)

    history_file = os.environ.get("HISTFILE") or str(Path.home() / ".myshell_history")

    if os.path.isfile(history_file):
        with open(history_file) as f:
            for line in f:
                line = line.rstrip("\n")
                if line:
                    readline.add_history(line)

    def write_history():
        length = readline.get_current_history_length()
        with open(history_file, "w") as f:
            for i in range(1, length + 1):
                f.write(readline.get_history_item(i) + "\n")

    atexit.register(write_history)


def get_executables():
    executables = set()
    for path in os.environ["PATH"].split(os.pathsep):
        if not os.path.isdir(path):
            continue

        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                executables.add(file)

    return executables


def get_current_directory_files():
    return os.listdir(os.getcwd())


def get_files_in_directory(directory):
    search_dir = directory if directory else "."
    if not os.path.isdir(search_dir):
        return []

    return [
        name
        for name in os.listdir(search_dir)
        if not os.path.isdir(os.path.join(search_dir, name))
    ]


def get_directories_in_directory(directory):
    search_dir = directory if directory else "."
    if not os.path.isdir(search_dir):
        return []

    return [
        name
        for name in os.listdir(search_dir)
        if os.path.isdir(os.path.join(search_dir, name))
    ]


def get_directory_from_input(input_string):
    last_slash_idx = input_string.rfind("/")
    if last_slash_idx == -1:
        return ""
    return input_string[: last_slash_idx + 1]


def get_registered_completions(text):
    words = readline.get_line_buffer().split()
    command = words[0] if words else ""
    if command not in REGISTERED_COMPLETES:
        return []

    script = REGISTERED_COMPLETES[command]
    if text:
        previous_word = words[-2] if len(words) >= 2 else ""
    else:
        previous_word = words[-1] if words else ""

    comp_line = readline.get_line_buffer()
    env = {
        **os.environ,
        "COMP_LINE": comp_line,
        "COMP_POINT": str(readline.get_endidx()),
    }

    result = subprocess.run(
        [script, command, text, previous_word],
        capture_output=True,
        text=True,
        env=env,
    )

    return [line + " " for line in result.stdout.splitlines()]


def configure_autocomplete():
    readline.set_completer_delims(" \t\n")

    def completer(text, state):
        line = readline.get_line_buffer()
        is_first_word = line[: readline.get_begidx()].strip() == ""

        matches = []
        if is_first_word:
            cmds = list(AUTO_COMPLETE_COMMANDS) + list(get_executables())
            matches.extend([cmd + " " for cmd in cmds if cmd.startswith(text)])
        else:
            words = line.split()
            command = words[0] if words else ""
            if command in REGISTERED_COMPLETES:
                matches.extend(get_registered_completions(text))
            else:
                directory = get_directory_from_input(text)

                files = [directory + name for name in get_files_in_directory(directory)]
                matches.extend([file + " " for file in files if file.startswith(text)])

                directories = [
                    directory + name for name in get_directories_in_directory(directory)
                ]
                matches.extend(
                    [dir + "/" for dir in directories if dir.startswith(text)]
                )

        if state < len(matches):
            return matches[state]
        return None

    def display_matches(substitution, matches, longest_match_length):
        print()
        print("  ".join(sorted(match.strip() for match in matches)))
        print("$ " + readline.get_line_buffer(), end="", flush=True)
        if hasattr(readline, "redisplay"):
            readline.redisplay()

    readline.set_completer(completer)
    if hasattr(readline, "set_completion_display_matches_hook"):
        readline.set_completion_display_matches_hook(display_matches)
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind("set bell-style audible")


def main():
    configure_autocomplete()
    configure_history()

    while True:
        raw_line = input("$ ")
        if raw_line.strip() and hasattr(readline, "set_auto_history"):
            readline.add_history(raw_line)

        tokens = tokenize(raw_line)
        if not tokens:
            continue

        segments = split_pipeline(tokens)
        if len(segments) > 1:
            handle_pipeline_command([(segment[0], segment[1:]) for segment in segments])
        else:
            command, arguments = segments[0][0], segments[0][1:]
            command_dispatcher(command, arguments)

        handle_jobs_command(completed_only=True)


if __name__ == "__main__":
    main()
