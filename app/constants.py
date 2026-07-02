from enum import Enum

REDIRECTION_OPERATORS = [">", "1>", "2>", ">>", "1>>", "2>>"]

HANDLED_COMMANDS = [
    "echo",
    "exit",
    "type",
    "pwd",
    "cd",
    "complete",
    "jobs",
    "history",
    "declare",
]

AUTO_COMPLETE_COMMANDS = ["echo", "exit"]


class StdoutTarget(Enum):
    STDOUT = "stdout"
    FILE = "file"


class StdStreams(Enum):
    STDOUT = "stdout"
    STDERR = "stderr"
