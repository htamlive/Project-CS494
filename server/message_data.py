from dataclasses import dataclass
from socket import socket
from message import Message


@dataclass(init=True)
class MessageData:
    data: Message
    client_socket: socket | None
    client_address: tuple | None


@dataclass
class TickMessage:
    pass
