from client.event import ServerMessage, UserAnswer
from config.config import Operator
from message import (
    AnswerMessage,
    DisconnectMessage,
    JoinAckMessage,
    JoinDenyMessage,
    JoinMessage,
    Message,
    Operation,
    PlayersChangedMessage,
    QuestionMessage,
    ReadyChangeMessage,
    ReadyMessage,
    ResultMessage,
    StartGameMessage,
)
from mixins.message_receiver import MessageReceiver
from .event import UserEnterName, UserAnswer
from proxy import Proxy
import socket
import threading
from multiprocessing import SimpleQueue
from .client_state import Unconnected, AnsweringQuestion, WaitingForQuestionOrGameResult
import logging
import mixins

logger = logging.getLogger(__name__)


class Client(Proxy, mixins.MessageReceiver):
    def __init__(self, host, port):
        Proxy.__init__(self)
        self._message_queue = SimpleQueue()
        self._response_queue = SimpleQueue()
        self._state = Unconnected(self)
        self._points = 0
        self._position = 0
        self._race_length = 0
        self._name = ""
        self._number_of_ready_players = 0
        self._number_of_players = 0

        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        MessageReceiver.__init__(self, self.client_socket)
        self._connect()
        logger.info("Client initialized")

    @property
    def name(self):
        return self._name

    def init_race_length(self, race_length):
        self._race_length = race_length

    def update_points(self, points):
        self._points = points

    def update_position(self, position):
        logger.info("Updating position to %d", position)
        self._position = position

    def _receive_loop(self):
        while True:
            response = self._receive_message()
            self._message_queue.put(ServerMessage(response))

    def _connect(self):
        self.client_socket.connect((self.host, self.port))
        print("Connected to server.")
        threading.Thread(
            target=self._receive_loop, daemon=True
        ).start()  # Start a new thread for receiving messages

    def wait_for_response(self):
        return self._response_queue.get()

    def put_response(self, response):
        self._response_queue.put(response)

    def get_score(self):
        return self._position

    def set_state(self, state):
        self._state = state

    def send_message(self, message: Message):
        self.client_socket.send(message.pack())

    def wait_for_message(self):
        return self._message_queue.get()

    def gen_quest(self):
        message = self.wait_for_message()
        match message:
            case ServerMessage(QuestionMessage(first_number, second_number, operation)):
                match operation:
                    case 0x1:
                        operation = Operator.ADD
                    case 0x2:
                        operation = Operation.SUB
                    case 0x3:
                        operation = Operation.MUL
                    case 0x4:
                        operation = Operation.DIV
                return first_number, operation, second_number, None

    def is_game_started(self):
        if self._message_queue.empty():
            return False
        resp = self.wait_for_message()
        match resp:
            case ServerMessage(PlayersChangedMessage(n_players)):
                self._number_of_players = n_players
            case ServerMessage(ReadyChangeMessage(n_players)):
                self._number_of_ready_players = n_players
            case ServerMessage(StartGameMessage(race_length)):
                self._race_length = race_length
                return True
        return False

    def register(self, name, mode):
        self.send_message(JoinMessage(0, name))
        rs = self.wait_for_message()
        match rs:
            case ServerMessage(JoinAckMessage()):
                self._name = name
                return True
            case ServerMessage(JoinDenyMessage()):
                return False
            case _:
                raise Exception("Unexpected message type")

    def check_answer(self, answer, _):
        self.send_message(AnswerMessage(int(answer)))
        response = self.wait_for_message()
        match response:
            case ServerMessage(ResultMessage(answer, is_correct, new_pos)):
                if is_correct:
                    self._position = new_pos
                return is_correct

    def _receive_message(self):
        data = self.receive_message()
        logger.info("Received data: %s", data)
        msg = Message.unpack(data)
        logger.info("Received message: %s", msg)
        return msg

    def on_ready(self):
        self.send_message(message=ReadyMessage(True))

    def get_mode(self):
        """
        return the mode of the game
        """
        return self.current_mode

    def leave_game(self):
        """
        leave the game
        This function is used when the user clicks the leave button in waiting room or game play state
        """
        self.send_message(DisconnectMessage())

    def get_user_top(self):
        return 1

    def get_user_score(self, stored_score):
        """
        You dont need to use the stored score. Just let it to match the calling
        """
        return self._position

    def init_time(self):
        """
        Initialize the time for the user when the game starts
        """
        self.time_left = 15
        return self.time_left

    def get_time_left(self):
        return self.time_left

    def get_number_of_players(self):
        return self._number_of_players

    def get_number_of_ready_players(self):
        return self._number_of_ready_players
