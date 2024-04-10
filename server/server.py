from __future__ import annotations
from abc import ABC, abstractmethod
from message import *
from .player import Player
from .message_data import MessageData, TickMessage
from .config import *
from .game import Game

import socket
import queue
import threading
import time
import random

from .states.server_state import State
from .states.waiting_state import WaitingState


# Define the server class
class GameServer:
    _state: State

    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.players = {}  # Dictionary to store connected players
        self.message_queue = queue.Queue()  # Queue for inter-thread communication
        self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
        self.transition_to(WaitingState())
        self.current_game: Game | None = None

    def transition_to(self, state: State):
        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self

    def start(self):
        # Start a thread for processing messages
        threading.Thread(target=self.process_messages, daemon=True).start()

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(MAX_CLIENTS)
        print("Server started on {}:{}".format(self.host, self.port))

        # Start the timer thread
        self.timer_thread.start()

        while True:
            client_socket, client_address = self.server_socket.accept()
            print("client_socket:", client_socket)
            print("client_address:", client_address)

            print("New connection from:", client_address)

            # Start a new thread to handle the client
            threading.Thread(
                target=self.handle_client, args=(client_socket, client_address)
            ).start()

    def handle_client(self, client_socket, client_address):
        # Receive messages from the client and put them into the message queue
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                # Put received message into the queue
                self.message_queue.put(
                    MessageData(Message.unpack(data), client_socket, client_address)
                )
            except Exception as e:
                print("Error receiving message:", e)
                break

        # Close the client socket
        self.message_queue.put(
            MessageData(DisconnectMessage(), client_socket, client_address)
        )

    def timer_loop(self):
        # Timer loop to send 'tick' message into the queue
        while True:
            self.message_queue.put(TickMessage())
            time.sleep(1)

    def process_messages(self):
        # Process messages from the queue and handle server logic based on the current state
        while True:
            # try:
            data_pack = self.message_queue.get()
            self._state.handle(data_pack)

            # except Exception as e:
            #     print("Error processing message:", e)
            #     continue
