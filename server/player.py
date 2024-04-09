from dataclasses import dataclass
from socket import socket


@dataclass(init=False)
class Player:
    """
    Player class to store player's information
    """

    name: str
    client_socket: socket
    client_address: tuple

    def __init__(self, name, client_socket, client_address):
        self.name = name
        self.client_socket = client_socket
        self.client_address = client_address
        self.ready = False

        self.score = 0
        self.position = 1
        self.current_answer: int | None = None
        self.answer_time: int | None = None
        self.nums_of_wrong_answers = 0
