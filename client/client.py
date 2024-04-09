from client.event import ServerMessage, UserAnswer
from config.config import Operator
from message import Message, Operation
from .event import UserEnterName, UserAnswer
from proxy import Proxy
import socket
import threading
from multiprocessing import SimpleQueue
from .client_state import Unconnected, AnsweringQuestion, WaitingForQuestion
import logging

logger = logging.getLogger(__name__)


class Client(Proxy):
    def __init__(self, host, port):
        super().__init__()
        self._message_queue = SimpleQueue()
        self._response_queue = SimpleQueue()
        self._state = Unconnected(self)
        self._points = 0
        self._position = 0

        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect()
        logger.info("Client initialized")

    def update_points(self, points):
        self._points = points

    def update_position(self, position):
        self._position = position

    def wait_for_response(self):
        return self._response_queue.get()

    def put_response(self, response):
        self._response_queue.put(response)

    def get_score(self):
        return self._points

    def send_message(self, message: Message):
        self.client_socket.send(message.pack())

    def init_time(self):
        self.time_left = 15

    def wait_for_message(self):
        return self._message_queue.get()

    def gen_quest(self):
        while True:
            self._state.handle()
            match self._state:
                case AnsweringQuestion(_, operand1, operand2, operator):
                    print(f"Question: {operand1} {operator} {operand2}")
                    op = None
                    match operator:
                        case 0x1:
                            op = Operator.ADD
                        case 0x2:
                            op = Operator.SUBTRACT
                        case 0x3:
                            op = Operator.MULTIPLY
                        case 0x4:
                            op = Operator.DIVIDE
                        case _:
                            raise ValueError("Invalid operator")
                    return operand1, op, operand2, None

    def on_ready(self):
        while not isinstance(self._state, WaitingForQuestion):
            self._state.handle()

    def is_game_started(self):
        return isinstance(self._state, WaitingForQuestion)

    def register(self, name, mode):
        self._message_queue.put(UserEnterName(name))
        self._state.handle()
        rs = self.wait_for_response()
        return rs

    def _connect(self):
        self.client_socket.connect((self.host, self.port))
        print("Connected to server.")
        threading.Thread(
            target=self._receive_loop, daemon=True
        ).start()  # Start a new thread for receiving messages

    def set_state(self, state):
        self._state = state

    def check_answer(self, answer, _):
        self._message_queue.put(UserAnswer(int(answer)))

    def _receive_message(self):
        data = self.client_socket.recv(4096)
        logger.info("Received data: %s", data)
        msg = Message.unpack(data)
        logger.info("Received message: %s", msg)
        return msg

    def on_update(self, delta_time):
        pass

    def _receive_loop(self):
        while True:
            try:
                response = self._receive_message()
                self._message_queue.put(ServerMessage(response))
                # if response.type in self.message_handlers:
                #     self.message_handlers[response.type](response)
                # else:
                #     print("Unhandled message type:", response.type)
            except Exception as e:
                print("Error receiving message:", e)
                break
