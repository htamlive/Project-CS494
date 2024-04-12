SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Racing Area - The wizard world"
DEFAULT_TIME = 5
SERVER_ADDR = "localhost"

from enum import Enum


class Mode(Enum):
    TRADITIONAL = 1
    BLITZ = 2


class Operator(Enum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MOD = "%"


class Result(Enum):
    CORRECT = "Correct"
    INCORRECT = "Incorrect"
    DISQUALIFIED = "Disqualified"


class Summary_type(Enum):
    WINNER = "Winner"

    DISQUALIFIED = "Disqualified"  # Use for consistent in the SummaryState


class Socket_return(Enum):
    IS_WAITING = "is_waiting"
