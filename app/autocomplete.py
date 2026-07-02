import os
import readline
import subprocess

from .commands import REGISTERED_COMPLETES
from .constants import AUTO_COMPLETE_COMMANDS


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

                directories = [directory + name for name in get_directories_in_directory(directory)]
                matches.extend([dir + "/" for dir in directories if dir.startswith(text)])

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
        name for name in os.listdir(search_dir) if not os.path.isdir(os.path.join(search_dir, name))
    ]


def get_directories_in_directory(directory):
    search_dir = directory if directory else "."
    if not os.path.isdir(search_dir):
        return []

    return [
        name for name in os.listdir(search_dir) if os.path.isdir(os.path.join(search_dir, name))
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
    previous_word = (words[-2] if len(words) >= 2 else "") if text else (words[-1] if words else "")

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
