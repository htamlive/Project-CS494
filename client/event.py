from dataclasses import dataclass
from message import Message


@dataclass
class Event:
    pass

@dataclass
class UserEnterName(Event):
    name: str


@dataclass
class UserAnswer(Event):
    answer: int

@dataclass
class UserReady(Event):
    pass

@dataclass
class ServerMessage(Event):
    message: Message
