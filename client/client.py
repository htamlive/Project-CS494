from client.event import ServerMessage, UserAnswer
from config.config import Socket_return, Operator, Result
from message import (
    AnswerMessage,
    DisconnectMessage,
    DisqualifiedMessage,
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
    TimeOutMessage,
    WinnerMessage,
)
from proxy import Proxy
import socket
import threading
from multiprocessing import SimpleQueue
import logging
import utils

logger = logging.getLogger(__name__)


class Client(Proxy):
    def __init__(self, host, port):
        Proxy.__init__(self)
        self._message_queue = SimpleQueue()
        self._response_queue = SimpleQueue()
        self._position = 1
        self._race_length = 0
        self._name = ""
        self._number_of_ready_players = 0
        self._number_of_players = 0
        self._remaining_players = 0

        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiver = utils.MessageReceiver(self.client_socket)
        self._connect()
        self._temp_msgs = []
        logger.info("Client initialized")

    def receive_message(self):
        return self.receiver.receive_message()

    @property
    def name(self):
        return self._name

    def update_position(self, position):
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

    def _receive_message(self):
        data = self.receive_message()
        logger.info("Received data: %s", data)
        msg = Message.unpack(data)
        logger.info("Received message: %s", msg)
        return msg

    def get_score(self):
        return self._position

    def send_message(self, message: Message):
        self.client_socket.send(message.pack())

    def wait_for_message(self):
        return self._message_queue.get()

    # ================== Proxy methods ================== #

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
                raise Exception("Unexpected message type %s", rs)

    def gen_quest(self):
        if self._message_queue.empty():
            return Socket_return.IS_WAITING
        message = self.wait_for_message()
        match message:
            case ServerMessage(QuestionMessage(first_number, second_number, operation)):
                self.init_time()
                match operation:
                    case 0x1:
                        operation = Operator.ADD
                    case 0x2:
                        operation = Operator.SUBTRACT
                    case 0x3:
                        operation = Operator.MULTIPLY
                    case 0x4:
                        operation = Operator.DIVIDE
                return first_number, operation, second_number, None

        return Socket_return.IS_WAITING

    def on_ready(self):
        self.send_message(message=ReadyMessage(True))

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
            case _:
                raise Exception("Unexpected message type")

    def submit_answer(self, answer, _):
        print("Submitting answer")
        self.send_message(AnswerMessage(int(answer)))

    def check_result(self):
        print("Checking result")
        if self._message_queue.empty():
            return Socket_return.IS_WAITING
        response = self.wait_for_message()
        match response:
            case ServerMessage(DisqualifiedMessage()):
                return Result.DISQUALIFIED
            case ServerMessage(TimeOutMessage()):
                self._temp_msgs.append(response)
                return Socket_return.IS_WAITING
            case ServerMessage(
                ResultMessage(answer, is_correct, new_pos, remaining_players)
            ):
                match self._temp_msgs.pop(0):
                    case ServerMessage(TimeOutMessage()):
                        self._remaining_players = remaining_players
                        if is_correct:
                            self._position = new_pos
                        return Result.CORRECT if is_correct else Result.INCORRECT
                    case _:
                        raise Exception("Unexpected message type %s", response)
            case _:
                raise Exception("Unexpected message type %s", response)

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

    def request_racing_length(self):
        return self._race_length

    def get_user_score(self, stored_score):
        return self._position

    def init_time(self):
        self.time_left = 15
        return self.time_left

    def get_time_left(self):
        return self.time_left

    def get_number_of_players(self):
        return self._number_of_players

    def get_number_of_ready_players(self):
        return self._number_of_ready_players

    def get_number_of_players_in_game(self):
        return self._remaining_players

    def check_winner(self):
        if self._message_queue.empty():
            return Socket_return.IS_WAITING
        print("Checking winner")
        resp = self.wait_for_message()
        match resp:
            case ServerMessage(WinnerMessage(have_winner, winner_name)):
                if have_winner:
                    return winner_name
                return None
            case _:
                raise Exception("Unexpected message type")
