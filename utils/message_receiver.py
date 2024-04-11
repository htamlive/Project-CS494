from message import MessageType, associated_classes


class MessageReceiver:
    def __init__(self, socket):
        self.socket = socket
        self.current_buffer = bytes()

    def receive_message(self):
        if len(self.current_buffer) < 1:
            self.current_buffer = self.socket.recv(4096)
            data = self.current_buffer
        else:
            data = self.current_buffer
        message_type = MessageType(data[0])
        length = associated_classes[message_type].length()
        while len(self.current_buffer) < length:
            self.current_buffer += data
            data = self.socket.recv(4096)
        data = self.current_buffer[:length]
        self.current_buffer = self.current_buffer[length:]
        return data
