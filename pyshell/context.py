from dataclasses import dataclass, field

from pyshell.execution.jobs import JobTable


@dataclass
class ShellContext:
    """Per-session state, passed explicitly."""

    declared_vars: dict = field(default_factory=dict)
    completions: dict = field(default_factory=dict)
    jobs: JobTable = field(default_factory=JobTable)
    exit_status: int = 0
    history_append_offset: int = 0
