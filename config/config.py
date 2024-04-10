SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Racing Area - The wizard world"
DEFAULT_TIME = 5

from enum import Enum

class Mode(Enum):
    TRADITIONAL = 1
    BLITZ = 2

class Operator(Enum):
    ADD = '+'
    SUBTRACT = '-'
    MULTIPLY = '*'
    DIVIDE = '/'
    MOD = '%'

class Result(Enum):
    CORRECT = 'Correct'
    INCORRECT = 'Incorrect'
    DISQUALIFIED = 'Disqualified'

class SOCKET_RETURN(Enum):
    IS_WAITING = 'is_waiting'