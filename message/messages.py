from dataclasses import dataclass
from enum import Enum


class Operation(Enum):
    ADD = 0x1
    SUB = 0x1
    MUL = 0x2
    DIV = 0x3


@dataclass(frozen=True)
class JoinMessage:
    room: int
    name: str


@dataclass(frozen=True)
class JoinDenyMessage:
    pass


@dataclass(frozen=True)
class JoinAckMessage:
    pass


@dataclass(frozen=True)
class ReadyMessage:
    state: bool


@dataclass(frozen=True)
class StartGameMessage:
    race_lenght: int


@dataclass(frozen=True)
class QuestionMessage:
    first_number: int
    second_number: int
    operation: Operation


@dataclass(frozen=True)
class TimeOutMessage:
    pass
