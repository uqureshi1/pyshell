try:
    import readline
except ImportError:
    import pyreadline3 as readline  # Windows fallback

from pyshell import builtins  # noqa: F401  (imports register every builtin)
from pyshell.autocomplete import configure_autocomplete
from pyshell.context import ShellContext
from pyshell.execution.executor import dispatch, run_pipeline
from pyshell.execution.redirection import output_to_target
from pyshell.history import configure_history
from pyshell.tokenizer import split_pipeline, tokenize


class Shell:
    """Owns the session state and the read-eval loop."""

    def __init__(self):
        self.ctx = ShellContext()
        configure_autocomplete(self.ctx)
        configure_history()

    def run(self):
        while True:
            raw_line = input("$ ")
            self._record_history(raw_line)
            self.run_line(raw_line)

    def run_line(self, raw_line):
        tokens = tokenize(raw_line, self.ctx)
        if tokens:
            segments = split_pipeline(tokens)
            if len(segments) > 1:
                run_pipeline([(segment[0], segment[1:]) for segment in segments], self.ctx)
            else:
                command, arguments = segments[0][0], segments[0][1:]
                dispatch(command, arguments, self.ctx)

        self._reap_jobs()

    def _record_history(self, raw_line):
        if raw_line.strip() and hasattr(readline, "set_auto_history"):
            readline.add_history(raw_line)

    def _reap_jobs(self):
        for line in self.ctx.jobs.render(completed_only=True):
            output_to_target(line)
