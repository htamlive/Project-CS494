from __future__ import annotations
from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass
from message import *
from .event import *

logger = logging.getLogger(__name__)


class ClientState(ABC):
    @abstractmethod
    def handle(self):
        pass


@dataclass
class Unconnected(ClientState):
    context: Client

    def __post_init__(self):
        logger.info("Transitioning to Unconnected state")

    def handle(self):
        message = self.context.wait_for_message()
        print("Received message: ", message)
        match message:
            case UserEnterName(name):
                print("Sending join message")
                self.context.send_message(JoinMessage(0, name))
                self.context.set_state(WaitingForGameStart(self.context))
            case _:
                logger.error("Unconnected: invalid event " + str(message))
                raise ValueError("Unconnected: invalid event " + str(message))
        message = self.context.wait_for_message()
        match message:
            case ServerMessage(JoinAckMessage()):
                self.context.set_state(WaitingForGameStart(self.context))
                self.context.update_position(0)
                self.context.put_response(True)
            case ServerMessage(JoinDenyMessage()):
                self.context.set_state(Unconnected(self.context))
                self.context.put_response(False)
            case _:
                logger.error("Unconnected: invalid event " + str(message))
                raise ValueError("Unconnected: invalid event " + str(message))


@dataclass
class WaitingForGameStart(ClientState):
    context: Client

    def __post_init__(self):
        logger.info("Transitioning to WaitingForGameStart state")

    def handle(self):
        inp = input("Press enter to start the game: ")
        self.context.send_message(ReadyMessage(True))
        self.context.set_state(WaitForOtherPlayers(self.context))


@dataclass
class WaitForOtherPlayers(ClientState):
    context: Client

    def __post_init__(self):
        logger.info("Transitioning to WaitForOtherPlayers state")

    def handle(self):
        message = self.context.wait_for_message()
        logger.info("Received message: %s", message)
        match message:
            case ServerMessage(StartGameMessage()):
                self.context.set_state(WaitingForQuestion(self.context))
            case ServerMessage(ReadyChangeMessage()):
                self.context.set_state(WaitForOtherPlayers(self.context))
            case _:
                logger.error("WaitForOtherPlayers: invalid event " + str(message))
                self.context.set_state(WaitForOtherPlayers(self.context))


@dataclass
class WaitingForQuestion(ClientState):
    context: Client

    def __post_init__(self):
        logger.info("Transitioning to WaitingForQuestion state")

    def handle(self):
        message = self.context.wait_for_message()
        logger.info("Received message: %s", message)
        match message:
            case ServerMessage(
                message=QuestionMessage(first_number, second_number, operation)
            ):
                self.context.set_state(
                    AnsweringQuestion(
                        self.context, first_number, second_number, operation
                    )
                )
            case _:
                raise ValueError("WaitingForQuestion: invalid event " + str(message))


@dataclass
class AnsweringQuestion(ClientState):
    context: Client
    operand1: int
    operand2: int
    operation: Operation

    def __post_init__(self):
        logger.info("Transitioning to AnsweringQuestion state")

    def handle(self):
        message = self.context.wait_for_message()
        match message:
            case UserAnswer(answer):
                self.context.send_message(
                    AnswerMessage(self.operand1, self.operand2, self.operation, answer)
                )
                logger.info("Sent answer")
                self.context.set_state(WaitingForResult(self.context))
            case _:
                raise ValueError("AnsweringQuestion: invalid event " + str(message))


@dataclass
class WaitingForResult(ClientState):
    context: Client

    def __post_init__(self):
        logger.info("Transitioning to WaitingForResult state")

    def handle(self):
        message = self.context.wait_for_message()
        logger.info("Received message: %s", message)
        match message:
            case ServerMessage(ResultMessage(answer, is_correct, new_pos)):
                if is_correct:
                    print(str(answer) + " is correct!")
                self.context.update_position(new_pos)
                self.context.set_state(WaitingForQuestion(self.context))
            case ServerMessage(TimeOutMessage()):
                self.context.set_state(WaitingForResult(self.context))
            case _:
                raise ValueError("WaitingForResult: invalid event " + str(message))


class GameOver(ClientState):
    context: Client

    def on_received(self, message):
        match message:
            case "GAME_OVER":
                return Unconnected(self.context)
            case _:
                return self
        while True:
            self._handle_message()
