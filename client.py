import tkinter as tk
import threading
import socket
from message import *

class GameClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.root = tk.Tk()
        self.root.title("Game Client")
        self.root.geometry("300x400")

        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack(pady=10)

        self.answer_entry = tk.Entry(self.root)
        self.answer_entry.pack(pady=10)

        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect)
        self.connect_button.pack(pady=5)

        self.join_button = tk.Button(self.root, text="Join Game", command=self.join_game)
        self.join_button.pack(pady=5)

        self.ready_button = tk.Button(self.root, text="Ready", command=self.ready)
        self.ready_button.pack(pady=5)

        self.answer_button = tk.Button(self.root, text="Answer", command=self.answer)
        self.answer_button.pack(pady=5)


        # Message handler map
        # self.message_handlers = {
        #     MessageType.JOIN_ACK: self.handle_join_ack,
        #     MessageType.JOIN_DENY: self.handle_join_deny,
        #     MessageType.START_GAME: self.handle_start_game,
        #     MessageType.READY: self.handle_ready
        # }

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        print("Connected to server.")
        threading.Thread(target=self.receive_loop, daemon=True).start()  # Start a new thread for receiving messages

    def send_message(self, message):
        self.client_socket.send(message.pack())

    def receive_message(self):
        data = self.client_socket.recv(4096)
        print("Received data:", data)
        print("Unpacked data type:", Message.unpack(data).type)
        print("Unpacked data:", Message.unpack(data).__dict__)
        return Message.unpack(data)

    def join_game(self):
        self.name = self.name_entry.get()
        print("Joining game with name:", self.name)
        # self.join_button.config(state=tk.DISABLED)
        join_message = JoinMessage(room=0x1111, name=self.name)
        self.send_message(join_message)

    def ready(self):
        print("ready")
        # self.ready_button.config(state=tk.DISABLED)
        ready_message = ReadyMessage(True)
        self.send_message(ready_message)
    
    def answer(self):
        answer = self.answer_entry.get()
        print("Answering question with:", answer)
        answer_message = AnswerMessage(int(answer))
        self.send_message(answer_message)

    def receive_loop(self):
        while True:
            try:
                response = self.receive_message()
                print(response.__dict__)
                # if response.type in self.message_handlers:
                #     self.message_handlers[response.type](response)
                # else:
                #     print("Unhandled message type:", response.type)
            except Exception as e:
                print("Error receiving message:", e)
                break

    # def handle_join_ack(self, response):
    #     messagebox.showinfo("Join Game", "Join successful!")
    #     self.ready_button.config(state=tk.NORMAL)

    # def handle_join_deny(self, response):
    #     messagebox.showerror("Join Game", "Join denied.")

    # def handle_start_game(self, response):
    #     messagebox.showinfo("Ready", "Game started!")

    # def handle_ready(self, response):
    #     # Handle ReadyMessage, if needed
    #     pass

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 4000
    # PLAYER_NAME = "Alice"  # Change this to the desired player name
    client = GameClient(HOST, PORT)
    client.start()
