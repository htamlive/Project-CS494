import struct
from .messages import *
from .message_type import *


class MessageEncoder:
    @staticmethod
    def encode(msg):
        match msg:
            case JoinMessage(room, name):
                name_bytes = name.encode()
                return struct.pack("<BI6s", MessageType.JOIN.value, room, name_bytes)
            case JoinDenyMessage():
                return struct.pack("<B", MessageType.JOIN_DENY.value)
            case JoinAckMessage():
                return struct.pack("<B", MessageType.JOIN_ACK.value)
            case ReadyMessage(state):
                return struct.pack("<B?", MessageType.READY.value, state)
            case StartGameMessage(legth):
                return struct.pack("<BB", MessageType.START_GAME.value, legth)
            case QuestionMessage(first_number, second_number, operation):
                return struct.pack(
                    "<BiiB",
                    MessageType.QUESTION.value,
                    first_number,
                    second_number,
                    operation.value,
                )
            case TimeOutMessage():
                return struct.pack("<B", MessageType.TIMEOUT.value)
            case _:
                raise ValueError("Unknown message type")
