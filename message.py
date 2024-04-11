from __future__ import annotations
import struct
from enum import Enum
from dataclasses import dataclass


class MessageType(Enum):
    JOIN = 0x1
    JOIN_DENY = 0x2
    JOIN_ACK = 0x3
    START_GAME = 0x4
    QUESTION = 0x5
    TIMEOUT = 0x6
    ANSWER = 0x7
    READY = 0x8
    READY_CHANGE = 0x9
    RESULT = 0xA
    WINNER = 0xC
    DISQUALIFIED = 0xD
    DISCONNECT = 0xE
    PLAYERS_CHANGED = 0xF


@dataclass
class Message:
    def __init__(self):
        pass

    def pack(self):
        raise NotImplementedError

    @classmethod
    def length(cls):
        return struct.calcsize(cls.format)

    @classmethod
    def unpack(cls, data):
        message_type = MessageType(data[0])
        for subclass in cls.__subclasses__():
            if subclass.type == message_type:
                return subclass.unpack_data(data)
        raise ValueError("Unknown message type")

    @classmethod
    def unpack_data(cls, data):
        raise NotImplementedError


@dataclass
class JoinMessage(Message):
    type = MessageType.JOIN
    format = "<BI10s"

    room: int
    name: str

    def __post_init__(self):
        super().__init__()

    def pack(self):
        name_bytes = self.name.encode()
        return struct.pack(self.format, self.type.value, self.room, name_bytes)

    @classmethod
    def unpack_data(cls, data):
        _, room, name = struct.unpack(cls.format, data)
        name = name.decode().rstrip("\x00")  # Decode and strip null bytes
        return cls(room, name)


@dataclass
class JoinDenyMessage(Message):
    type = MessageType.JOIN_DENY
    format = "<B"

    def __init__(self):
        super().__init__()

    def pack(self):
        return struct.pack(self.format, self.type.value)

    @classmethod
    def unpack_data(cls, data):
        return cls()


@dataclass
class JoinAckMessage(Message):
    type = MessageType.JOIN_ACK
    format = "<B"

    def __init__(self):
        super().__init__()

    def pack(self):
        return struct.pack(self.format, self.type.value)

    @classmethod
    def unpack_data(cls, data):
        return cls()


@dataclass
class ReadyMessage(Message):
    type = MessageType.READY
    format = "<B?"

    state: bool

    def __post_init__(self):
        super().__init__()

    def pack(self):
        return struct.pack(self.format, self.type.value, self.state)

    @classmethod
    def unpack_data(cls, data):
        _, state = struct.unpack(cls.format, data)
        return cls(state)


@dataclass
class ReadyChangeMessage(Message):
    type = MessageType.READY_CHANGE
    format = "<B10s?"

    player_name: str
    is_ready: bool

    def __post_init__(self):
        super().__init__()

    def pack(self):
        name_bytes = self.player_name.encode()
        return struct.pack(self.format, self.type.value, name_bytes, self.is_ready)

    @classmethod
    def unpack_data(cls, data):
        _, player_name, is_ready = struct.unpack(cls.format, data)
        player_name = player_name.decode().rstrip("\x00")
        return cls(player_name, is_ready)


@dataclass
class StartGameMessage(Message):
    type = MessageType.START_GAME
    format = "<BB"

    race_lenght: int

    def __post_init__(self):
        super().__init__()

    def pack(self):
        return struct.pack(self.format, self.type.value, self.race_lenght)

    @classmethod
    def unpack_data(cls, data):
        _, race_lenght = struct.unpack(cls.format, data)
        return cls(race_lenght)


class Operation(Enum):
    ADD = 0x1
    SUB = 0x2
    MUL = 0x3
    DIV = 0x4


@dataclass
class QuestionMessage(Message):
    type = MessageType.QUESTION
    format = "<BiiB"

    first_number: int
    second_number: int
    operation: Operation

    def __post_init__(self):
        super().__init__()

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


@dataclass
class TimeOutMessage(Message):
    type = MessageType.TIMEOUT
    format = "<B"

    def __init__(self):
        super().__init__()

    def pack(self):
        return struct.pack(self.format, self.type.value)

    @classmethod
    def unpack_data(cls, data):
        return cls()


@dataclass
class AnswerMessage(Message):
    type = MessageType.ANSWER
    format = "<Bi"

    answer: int

    def __post_init__(self):
        super().__init__()

    def pack(self):
        return struct.pack(self.format, self.type.value, self.answer)

    @classmethod
    def unpack_data(cls, data):
        _, answer = struct.unpack(cls.format, data)
        return cls(answer)


@dataclass
class ResultMessage(Message):
    type = MessageType.RESULT
    format = "<B10si?ii"

    player_name: str
    answer: int
    is_correct: bool
    new_pos: int
    remain_players: int

    def __post_init__(self):
        super().__init__()

    def pack(self):
        return struct.pack(
            self.format,
            self.type.value,
            self.player_name.encode(),
            self.answer,
            self.is_correct,
            self.new_pos,
            self.remain_players,
        )

    @classmethod
    def unpack_data(cls, data):
        _, player_name, answer, is_correct, new_pos, remain = struct.unpack(
            cls.format, data
        )
        player_name = player_name.decode().rstrip("\x00")
        return cls(player_name, answer, is_correct, new_pos, remain)


@dataclass
class WinnerMessage(Message):
    type = MessageType.WINNER
    format = "<B?10s"

    have_winner: bool
    name: str

    def pack(self):
        name_bytes = self.name.encode()
        return struct.pack(self.format, self.type.value, self.have_winner, name_bytes)

    @classmethod
    def unpack_data(cls, data):
        _, have_winner, name = struct.unpack(cls.format, data)
        name = name.decode().rstrip("\x00")
        return cls(have_winner, name)


class DisqualifiedMessage(Message):
    type = MessageType.DISQUALIFIED
    format = "<B"

    def __init__(self):
        super().__init__()

    def pack(self):
        return struct.pack(self.format, self.type.value)

    @classmethod
    def unpack_data(cls, data):
        return cls()


@dataclass
class DisconnectMessage(Message):
    type = MessageType.DISCONNECT
    format = "<B"

    def pack(self):
        return struct.pack(self.format, self.type.value)

    @classmethod
    def unpack_data(cls, data):
        return cls()


@dataclass
class PlayersChangedMessage(Message):
    type = MessageType.PLAYERS_CHANGED
    format = "<B10s?"

    player_name: str
    is_join: bool

    def pack(self):
        name_bytes = self.player_name.encode()
        return struct.pack(self.format, self.type.value, name_bytes, self.is_join)

    @classmethod
    def unpack_data(cls, data):
        _, name_bytes, is_join = struct.unpack(cls.format, data)
        return cls(name_bytes.decode().rstrip("\x00"), is_join)


if __name__ == "__main__":
    # Example usage:
    join_message = JoinMessage(1234, "Alice")
    join_message_bytes = join_message.pack()
    print("Join Message:", join_message_bytes)
    print("Unpacked Join Message:", Message.unpack(join_message_bytes).__dict__)

    join_deny_message = JoinDenyMessage()
    join_deny_message_bytes = join_deny_message.pack()
    print("Join Deny Message:", join_deny_message_bytes)
    print(
        "Unpacked Join Deny Message:", Message.unpack(join_deny_message_bytes).__dict__
    )

    join_ack_message = JoinAckMessage()
    join_ack_message_bytes = join_ack_message.pack()
    print("Join Ack Message:", join_ack_message_bytes)
    print("Unpacked Join Ack Message:", Message.unpack(join_ack_message_bytes).__dict__)

    ready_message = ReadyMessage(True)
    ready_message_bytes = ready_message.pack()
    print("Ready Message:", ready_message_bytes)
    print("Unpacked Ready Message:", Message.unpack(ready_message_bytes).__dict__)

    start_game_message = StartGameMessage(100)
    start_game_message_bytes = start_game_message.pack()
    print("Start Game Message:", start_game_message_bytes)
    print(
        "Unpacked Start Game Message:",
        Message.unpack(start_game_message_bytes).__dict__,
    )

    question_message = QuestionMessage(1, 22, Operation(int(1)))
    question_message_bytes = question_message.pack()
    print("Question Message:", question_message_bytes)
    print("Unpacked Question Message:", Message.unpack(question_message_bytes).__dict__)


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

associated_classes = {
    MessageType.JOIN: JoinMessage,
    MessageType.JOIN_DENY: JoinDenyMessage,
    MessageType.JOIN_ACK: JoinAckMessage,
    MessageType.READY: ReadyMessage,
    MessageType.READY_CHANGE: ReadyChangeMessage,
    MessageType.START_GAME: StartGameMessage,
    MessageType.QUESTION: QuestionMessage,
    MessageType.TIMEOUT: TimeOutMessage,
    MessageType.ANSWER: AnswerMessage,
    MessageType.RESULT: ResultMessage,
    MessageType.WINNER: WinnerMessage,
    MessageType.DISQUALIFIED: DisqualifiedMessage,
    MessageType.DISCONNECT: DisconnectMessage,
    MessageType.PLAYERS_CHANGED: PlayersChangedMessage,
}
