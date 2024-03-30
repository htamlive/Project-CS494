from message import *
import tkinter as tk
from tkinter import messagebox
import threading
import socket
import struct

class GameClient:
    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.root = tk.Tk()
        self.root.title("Game Client")
        self.root.geometry("300x200")

        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect)
        self.connect_button.pack(pady=15)

        self.join_button = tk.Button(self.root, text="Join Game", command=self.join_game)
        self.join_button.pack(pady=10)

        self.ready_button = tk.Button(self.root, text="Ready", command=self.ready, state=tk.DISABLED)
        self.ready_button.pack(pady=5)

        # Message handler map
        self.message_handlers = {
            MessageType.JOIN_ACK: self.handle_join_ack,
            MessageType.JOIN_DENY: self.handle_join_deny,
            MessageType.START_GAME: self.handle_start_game,
            MessageType.READY: self.handle_ready
        }

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        print("Connected to server.")

    def send_message(self, message):
        self.client_socket.send(message.pack())

    def receive_message(self):
        data = self.client_socket.recv(1024)
        return Message.unpack(data)

    def join_game(self):
        print("join_game")
        self.join_button.config(state=tk.DISABLED)
        join_message = JoinMessage(room=0x1111, name=self.name)
        self.send_message(join_message)
        self.handle_response()

    def ready(self):
        print("ready")
        self.ready_button.config(state=tk.DISABLED)
        ready_message = ReadyMessage(True)
        self.send_message(ready_message)
        self.handle_response()

    def handle_response(self):
        response = self.receive_message()
        if response.type in self.message_handlers:
            self.message_handlers[response.type](response)
        else:
            messagebox.showerror("Error", "Unhandled message type: {}".format(response.type))
        self.join_button.config(state=tk.NORMAL)
        self.ready_button.config(state=tk.NORMAL)

    def handle_join_ack(self, response):
        messagebox.showinfo("Join Game", "Join successful!")
        self.ready_button.config(state=tk.NORMAL)

    def handle_join_deny(self, response):
        messagebox.showerror("Join Game", "Join denied.")

    def handle_start_game(self, response):
        messagebox.showinfo("Ready", "Game started!")

    def handle_ready(self, response):
        # Handle ReadyMessage, if needed
        pass

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 4000
    PLAYER_NAME = "Alice"  # Change this to the desired player name
    client = GameClient(HOST, PORT, PLAYER_NAME)
    client.start()
