from enum import Enum

REDIRECTION_OPERATORS = [">", "1>", "2>", ">>", "1>>", "2>>"]


class StdoutTarget(Enum):
    STDOUT = "stdout"
    FILE = "file"


class StdStreams(Enum):
    STDOUT = "stdout"
    STDERR = "stderr"
