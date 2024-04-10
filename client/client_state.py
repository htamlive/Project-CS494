from __future__ import annotations
from abc import ABC, abstractmethod
import enum
import logging
from dataclasses import dataclass
from message import *
from .event import *
import client.client as client

logger = logging.getLogger(__name__)


class EndGameStatus(enum.Enum):
    """
    Enum for the status of the game when it ends, whether the client won, was disqualified, or lost.
    """

    WIN = 1
    DISQUALIFIED = 2
    OTHER_WIN = 3


class ClientState(ABC):
    @abstractmethod
    def handle(self):
        pass


@dataclass
class Unconnected(ClientState):
    context: client.Client

    def __post_init__(self):
        logger.info("Transitioning to Unconnected state")

    def handle(self):
        # wait for user to enter name
        message = self.context.wait_for_message()
        logger.debug("Received message: %s", message)
        match message:
            case UserEnterName(name):
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
    context: client.Client

    def __post_init__(self):
        logger.info("Transitioning to WaitingForGameStart state")

    def handle(self):
        self.context.send_message(ReadyMessage(True))
        logger.info("Sent ready message")
        self.context.set_state(WaitForOtherPlayers(self.context))


@dataclass
class WaitForOtherPlayers(ClientState):
    context: client.Client

    def __post_init__(self):
        logger.info("Transitioning to WaitForOtherPlayers state")

    def handle(self):
        while True:
            logger.info("Waiting for other players")
            message = self.context.wait_for_message()
            logger.info("Received message: %s", message)
            match message:
                case ServerMessage(ReadyChangeMessage(n_ready)):
                    pass
                case ServerMessage(StartGameMessage(race_length)):
                    self.context.init_race_length(race_length)
                    self.context.set_state(WaitingForQuestionOrGameResult(self.context))
                    break
                case _:
                    logger.error("WaitForOtherPlayers: invalid event " + str(message))
                    raise ValueError(
                        "WaitForOtherPlayers: invalid event " + str(message)
                    )


@dataclass
class WaitingForQuestionOrGameResult(ClientState):
    context: client.Client

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
            case ServerMessage(WinnerMessage(winner)):
                logger.info("Received winner message")
                print(f"{winner} won!")
                if winner == self.context.name:
                    self.context.set_state(GameEnded(self.context, EndGameStatus.WIN))
                else:
                    self.context.set_state(
                        GameEnded(self.context, EndGameStatus.OTHER_WIN)
                    )
            case _:
                raise ValueError("WaitingForQuestion: invalid event " + str(message))


@dataclass
class AnsweringQuestion(ClientState):
    context: client.Client
    operand1: int
    operand2: int
    operation: Operation

    def __post_init__(self):
        logger.info("Transitioning to AnsweringQuestion state")

    def handle(self):
        message = self.context.wait_for_message()
        match message:
            case UserAnswer(answer):
                self.context.send_message(AnswerMessage(answer))
                logger.info("Sent answer")
                self.context.set_state(WaitingForResult(self.context, answer))
            case _:
                raise ValueError("AnsweringQuestion: invalid event " + str(message))


@dataclass
class WaitingForResult(ClientState):
    context: client.Client
    user_answer: int

    def __post_init__(self):
        logger.info("Transitioning to WaitingForResult state")

    def handle(self):
        message = self.context.wait_for_message()
        logger.info("Received message: %s", message)
        match message:
            case ServerMessage(TimeOutMessage()):
                logger.info("Other player all answered")
            case _:
                raise ValueError("Should recieve TimeOutMessage before ResultMessage")

        message = self.context.wait_for_message()

        match message:
            case ServerMessage(DisqualifiedMessage()):
                logger.info("Received disqualified message")
                self.context.set_state(
                    GameEnded(self.context, EndGameStatus.DISQUALIFIED)
                )
            case ServerMessage(ResultMessage(answer, is_correct, new_pos)):
                if is_correct:
                    print(str(self.user_answer) + " is CORRECT!")
                else:
                    print(str(self.user_answer) + " is WRONG!")
                self.context.update_position(new_pos)
                self.context.set_state(WaitingForQuestionOrGameResult(self.context))
            case _:
                raise ValueError("WaitingForResult: invalid event " + str(message))


@dataclass
class GameEnded(ClientState):
    context: client.Client
    status: EndGameStatus

    def __post_init__(self):
        logger.info("Transitioning to GameEnded state")

    def handle(self):
        pass
