import atexit
import os
from pathlib import Path
import readline


def configure_history():
    if hasattr(readline, "set_auto_history"):
        readline.set_auto_history(False)

    history_file = os.environ.get("HISTFILE") or str(Path.home() / ".pyshell_history")

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
