from abc import ABC, abstractmethod
from dataclasses import dataclass
import struct
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


class Message(ABC):
    type: MessageType

    @abstractmethod
    def pack(self):
        pass

    @classmethod
    def unpack(cls, data):
        message_type = MessageType(data[0])
        for subclass in cls.__subclasses__():
            if subclass.type == message_type:
                return subclass.unpack_data(data)
        raise ValueError("Unknown message type")

    @classmethod
    @abstractmethod
    def unpack_data(cls, data):
        pass


@dataclass(frozen=True)
class JoinMessage(Message):
    type = MessageType.JOIN
    format = "<BI6s"
    room: int
    name: str

    def pack(self):
        name_bytes = self.name.encode()
        return struct.pack(self.format, self.type.value, self.room, name_bytes)

    @classmethod
    def unpack_data(cls, data):
        _, room, name = struct.unpack(cls.format, data)
        name = name.decode().rstrip("\x00")  # Decode and strip null bytes
        return cls(room, name)


@dataclass(frozen=True)
class JoinDenyMessage(Message):
    type = MessageType.JOIN_DENY
    format = "<B"

    def pack(self):
        return struct.pack(self.format, self.type.value)

    @classmethod
    def unpack_data(cls, _):
        return cls()


@dataclass(frozen=True)
class JoinAckMessage(Message):
    type = MessageType.JOIN_ACK
    format = "<B"

    def pack(self):
        return struct.pack(self.format, self.type.value)

    @classmethod
    def unpack_data(cls, _):
        return cls()


@dataclass(frozen=True)
class ReadyMessage(Message):
    type = MessageType.READY
    format = "<B?"
    state: bool

    def pack(self):
        return struct.pack(self.format, self.type.value, self.state)

    @classmethod
    def unpack_data(cls, data):
        _, state = struct.unpack(cls.format, data)
        return cls(state)


@dataclass(frozen=True)
class StartGameMessage(Message):
    type = MessageType.START_GAME
    format = "<BB"
    race_lenght: int

    def pack(self):
        return struct.pack(self.format, self.type.value, self.race_lenght)

    @classmethod
    def unpack_data(cls, data):
        _, race_lenght = struct.unpack(cls.format, data)
        return cls(race_lenght)


class Operation(Enum):
    ADD = 0x1
    SUB = 0x1
    MUL = 0x2
    DIV = 0x3


@dataclass(frozen=True)
class QuestionMessage(Message):
    type = MessageType.QUESTION
    format = "<BiiB"
    first_number: int
    second_number: int
    operation: Operation

    def pack(self):
        return struct.pack(
            self.format,
            self.type.value,
            self.first_number,
            self.second_number,
            self.operation.value,
        )

    @classmethod
    def unpack_data(cls, data):
        _, first_number, second_number, operation = struct.unpack(cls.format, data)
        return cls(first_number, second_number, operation)


@dataclass(frozen=True)
class TimeOutMessage(Message):
    type = MessageType.TIMEOUT
    format = "<B"

    def pack(self):
        return struct.pack(self.format, self.type.value)

    @classmethod
    def unpack_data(cls, _):
        return cls()


if __name__ == "__main__":
    # Example usage:
    join_message = JoinMessage(1234, "Alice")
    join_message_bytes = join_message.pack()
    print("Join Message:", join_message_bytes)
    print("Unpacked Join Message:", Message.unpack(join_message_bytes))

    join_deny_message = JoinDenyMessage()
    join_deny_message_bytes = join_deny_message.pack()
    print("Join Deny Message:", join_deny_message_bytes)
    print("Unpacked Join Deny Message:", Message.unpack(join_deny_message_bytes))

    join_ack_message = JoinAckMessage()
    join_ack_message_bytes = join_ack_message.pack()
    print("Join Ack Message:", join_ack_message_bytes)
    print("Unpacked Join Ack Message:", Message.unpack(join_ack_message_bytes))

    ready_message = ReadyMessage(True)
    ready_message_bytes = ready_message.pack()
    print("Ready Message:", ready_message_bytes)
    print("Unpacked Ready Message:", Message.unpack(ready_message_bytes))

    start_game_message = StartGameMessage(100)
    start_game_message_bytes = start_game_message.pack()
    print("Start Game Message:", start_game_message_bytes)
    print("Unpacked Start Game Message:", Message.unpack(start_game_message_bytes))

    question_message = QuestionMessage(10, 20, Operation.ADD)
    question_message_bytes = question_message.pack()
    print("Question Message:", question_message_bytes)
    print("Unpacked Question Message:", Message.unpack(question_message_bytes))


# # Define the format strings for each message type
# JOIN_FORMAT = '<BIB6s'  # B: 1 byte, I: 4 bytes, 6s: 6 bytes
# JOIN_DENY_FORMAT = '<B'
# JOIN_ACK_FORMAT = '<B'
# READY_FORMAT = '<BB'  # BB: 2 bytes

# # Define the struct classes for each message type
# class JoinMessage:
#     def __init__(self, room, name):
#         self.type = 0x1
#         self.room = room
#         self.name = name

#     def pack(self):
#         return struct.pack(JOIN_FORMAT, self.type, self.room, len(self.name), self.name.encode())

#     def unpack(data):
#         type, room, name_len = struct.unpack(JOIN_FORMAT, data[:7])
#         name = struct.unpack(f'<{name_len}s', data[7:])[0].decode()
#         return JoinMessage(room, name)

# class JoinDenyMessage:
#     def __init__(self):
#         self.type = 0x2

#     def pack(self):
#         return struct.pack(JOIN_DENY_FORMAT, self.type)

# class JoinAckMessage:
#     def __init__(self):
#         self.type = 0x3

#     def pack(self):
#         return struct.pack(JOIN_ACK_FORMAT, self.type)

# class ReadyMessage:
#     def __init__(self, state):
#         self.type = 0x8
#         self.state = state

#     def pack(self):
#         return struct.pack(READY_FORMAT, self.type, self.state)

# # Example usage:
# room_id = 1234
# name = "Alice"
# join_message = JoinMessage(room_id, name)
# print("Join Message:", join_message.pack())

# join_deny_message = JoinDenyMessage()
# print("Join Deny Message:", join_deny_message.pack())

# join_ack_message = JoinAckMessage()
# print("Join Ack Message:", join_ack_message.pack())

# ready_message = ReadyMessage(1)
# print("Ready Message:", ready_message.pack())
