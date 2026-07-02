try:
    import readline
except ImportError:
    import pyreadline3 as readline  # Windows fallback

from .autocomplete import configure_autocomplete
from .commands import handle_jobs_command, handle_pipeline_command
from .dispatcher import command_dispatcher
from .history import configure_history
from .tokenizer import split_pipeline, tokenize


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
