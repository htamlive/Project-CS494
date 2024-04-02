import struct
from .messages import *
from .message_type import *


def decode(data):
    """
    This function is used to encode a message object into a byte array. Only type defined in messages.py are supported.
    """
    message_type = data[0]
    match message_type:
        case MessageType.JOIN.value:
            _, room, name = struct.unpack("<BI6s", data)
            name = name.decode().rstrip("\x00")
            return JoinMessage(room, name)
        case MessageType.JOIN_DENY.value:
            return JoinDenyMessage()
        case MessageType.JOIN_ACK.value:
            return JoinAckMessage()
        case MessageType.READY.value:
            _, state = struct.unpack("<B?", data)
            return ReadyMessage(state)
        case MessageType.START_GAME.value:
            _, legth = struct.unpack("<BB", data)
            return StartGameMessage(legth)
        case MessageType.QUESTION.value:
            _, first_number, second_number, operation = struct.unpack("<BiiB", data)
            return QuestionMessage(first_number, second_number, Operation(operation))
        case MessageType.TIMEOUT.value:
            return TimeOutMessage()
        case _:
            raise ValueError("Unknown message type")
