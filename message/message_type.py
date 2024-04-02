from enum import Enum


class MessageType(Enum):
    JOIN = 0x1
    JOIN_DENY = 0x2
    JOIN_ACK = 0x3
    READY = 0x8
    START_GAME = 0x4
    QUESTION = 0x5
    TIMEOUT = 0x6
    ANSWER = 0x7
    RESULT = 0xA
