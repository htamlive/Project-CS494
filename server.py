from message import *
import socket
import threading

class GameStates:
    WAITING = "waiting"
    START = "start"

class GameServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.clients = {}  # Dictionary to store client connections and information
        self.state = GameStates.WAITING # Game state

        # Message handler map
        self.message_handlers = {
            MessageType.JOIN: self.handle_join_message,
            MessageType.READY: self.handle_ready_message
        }

    def start(self):
        self.server_socket.listen(5)
        print("Server listening on {}:{}".format(self.host, self.port))
        while True:
            client_socket, client_address = self.server_socket.accept()
            print("New connection from:", client_address)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        print("Handling client:", client_socket)

        while True:
            try:
                data = client_socket.recv(1024)
                print("Received data:", data)
                if not data:
                    break
                message = Message.unpack(data)
                self.handle_message(client_socket, message)
            except Exception as e:
                print("Error handling client:", e)
                break
        self.handle_disconnect(client_socket)
        print("Closed connection:", client_socket)

    def handle_message(self, client_socket, message):
        print("Handling message:", message)
        if message.type in self.message_handlers:
            self.message_handlers[message.type](client_socket, message)
        else:
            print("Unhandled message type:", message.type)

    def handle_join_message(self, client_socket, message):
        print("Handling JoinMessage:", message)
        if self.state == "waiting" and len(self.clients) < MAX_PLAYERS:
            client_id = len(self.clients) + 1  # Generate unique client ID
            join_ack_message = JoinAckMessage()
            client_socket.send(join_ack_message.pack())
            client_name = message.name
            self.clients[client_id] = {"socket": client_socket, "name": client_name, "ready": False}
            print("Player {} joined as {}".format(client_id, client_name))
        else:
            join_deny_message = JoinDenyMessage()
            client_socket.send(join_deny_message.pack())

    def handle_ready_message(self, client_socket, message):
        print("Handling ReadyMessage:", message)
        client_id = self.get_client_id(client_socket)
        if client_id is not None:
            self.clients[client_id]["ready"] = True
            ready_count = sum(client["ready"] for client in self.clients.values())
            for client_data in self.clients.values():
                client_data["socket"].send(ReadyMessage(ready_count).pack())
            if ready_count == len(self.clients):
                self.start_game()

    def start_game(self):
        print("Starting game...")
        # Start the game
        self.state = "start"
        for client_data in self.clients.values():
            client_data["socket"].send(StartGameMessage(3).pack())

    def handle_disconnect(self, client_socket):
        client_id = self.get_client_id(client_socket)
        if client_id is not None:
            del self.clients[client_id]
            print("Client disconnected:", client_id)

    def get_client_id(self, client_socket):
        for client_id, client_data in self.clients.items():
            if client_data["socket"] == client_socket:
                return client_id
        return None

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 4000
    MAX_PLAYERS = 4  # Maximum number of players allowed in the game
    server = GameServer(HOST, PORT)
    server.start()
