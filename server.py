from __future__ import annotations
from abc import ABC, abstractmethod
from message import *

import socket
import threading
import queue
import time
import random

# Define constants
HOST = 'localhost'
PORT = 4000
MAX_CLIENTS = 10
MAX_PLAYERS = 4
QUESTION_TIME_LIMIT = 30  # Time limit for answering a question (in seconds)
NUMS_OF_QUESTIONS = 50  # Number of questions in a game
RACE_LENGTH = 5

class Player:
    def __init__(self, name, client_socket, client_address):
        self.name = name
        self.client_socket = client_socket
        self.client_address = client_address
        self.ready = False

        self.score = 0
        self.position = 1
        self.current_answer : int = None
        self.answer_time : int = None 
        self.nums_of_wrong_answers = 0

class Game:
    def __init__(self, race_length, players):
        self.race_length = race_length
        self.players = players
        self.current_index = -1
        self.question = []
        self.remaining_time = -1

    def new_question(self):
        # create random question
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        # operation = random.randint(1, 4)
        operation = int(1)

        return QuestionMessage(num1, num2, Operation(operation))

    def new_question_list(self):
        for _ in range(NUMS_OF_QUESTIONS):
            self.question.append(self.new_question())


class State(ABC):
    @property
    def context(self) -> GameServer:
        return self._context

    @context.setter
    def context(self, context: GameServer) -> None:
        self._context = context

    @abstractmethod
    def handle_join(self, data_pack) -> None:
        pass

    @abstractmethod
    def handle_ready(self, data_pack) -> None:
        pass

    @abstractmethod
    def handle_answer(self, data_pack) -> None:
        pass

    @abstractmethod
    def handle_tick(self, data_pack) -> None:
        pass

    @abstractmethod
    def handle_disconnect(self, data_pack) -> None:
        pass

class WaitingState(State):
    def handle_join(self, data_pack) -> None:
        message: JoinMessage = Message.unpack(data_pack[0])
        client_socket = data_pack[1]
        client_address = data_pack[2]

        print("Join message:", message.__dict__)
        
        player_name = message.name
        if client_address in self.context.players or len(self.context.players) == MAX_PLAYERS or any(player.name == player_name for player in self.context.players.values()):
            client_socket.send(JoinDenyMessage().pack())
            return
        
        print("Player joined:", player_name)
        self.context.players[client_address] = Player(player_name, client_socket, client_address)
        client_socket.send(JoinAckMessage().pack())

    def handle_ready(self, data_pack) -> None:
        client_address = data_pack[2]
        # Check if the player is already in the players dictionary
        if client_address not in self.context.players:
            return

        # Check if the player is already ready
        player = self.context.players[client_address]
        if player.ready:
            return
        
        player.ready = True

        # Get number of ready players
        ready_players = sum(1 for player in self.context.players.values() if player.ready)

        # Broadcast the ready message to all players
        for address, player in self.context.players.items():
            player.client_socket.send(ReadyChangeMessage(ready_players).pack())
        
        # Check if all players are ready
        if ready_players == len(self.context.players):
            # Broadcast the start game message to all players
            for address, player in self.context.players.items():
                player.client_socket.send(StartGameMessage(RACE_LENGTH).pack())

            # Start the game
            self.context.transition_to(StartingState())

            print("Game started!")

    def handle_answer(self, data_pack) -> None:
        return

    def handle_tick(self, data_pack) -> None:
        return

    def handle_disconnect(self, data_pack) -> None:
        client_address = data_pack[2]
        if client_address in self.context.players:
            del self.context.players[client_address]

        # # Broadcast the player disconnected message to all players
        # for address, player in self.context.players.items():
        #     player.client_socket.send(PlayerDisconnectedMessage().pack())

        print("Player disconnected.")


class StartingState(State):
    def handle_join(self, data_pack) -> None:
        return

    def handle_ready(self, data_pack) -> None:
        return

    def handle_answer(self, data_pack) -> None:
        message: AnswerMessage = Message.unpack(data_pack[0])
        client_address = data_pack[2]
        if self.context.current_game.remaining_time == -1:
            return

        if client_address not in self.context.current_game.players:
            return

        answer = message.answer
        player = self.context.current_game.players[client_address]
        player.current_answer = answer
        player.answer_time = time.time_ns()

    def handle_tick(self, data_pack):

        if self.context.current_game == None:
            # Create a new game
            self.context.current_game = Game(RACE_LENGTH, self.context.players)
            self.context.current_game.new_question_list()
            self.context.current_game.remaining_time = -1
            self.context.current_game.current_index = -1

            print("New game created.")

        if self.context.current_game.remaining_time == -1:
            # New question
            self.context.current_game.current_index += 1

            # Reset answers
            for player in self.context.current_game.players.values():
                player.current_answer = None
                player.answer_time = None

            # Broadcast the question to all players
            for address, player in self.context.current_game.players.items():
                player.client_socket.send(self.context.current_game.question[self.context.current_game.current_index].pack())
                print("Sent question:", self.context.current_game.question[self.context.current_game.current_index].__dict__)
            
            self.context.current_game.remaining_time = QUESTION_TIME_LIMIT
        else:
            self.context.current_game.remaining_time -= 1

            if self.context.current_game.remaining_time == 0 or all(player.current_answer is not None for player in self.context.current_game.players.values()):
                # Broadcast the time out message to all players
                for address, player in self.context.current_game.players.items():
                    player.client_socket.send(TimeOutMessage().pack())
                    print("Sent time out message.")
                
                # Start checking the answers
                correct_answer = None
                correct_index = self.context.current_game.current_index
                fastest_player = None
                fastest_time = float('inf')
                total_points_lost = 0
                disqualified_players = []

                # Calculate the correct answer and find the fastest player
                num1 = self.context.current_game.question[correct_index].first_number
                num2 = self.context.current_game.question[correct_index].second_number
                operation = self.context.current_game.question[correct_index].operation

                correct_answer = num1 + num2 if operation == Operation.ADD else num1 - num2 if operation == Operation.SUB else num1 * num2 if operation == Operation.MUL else num1 / num2

                for address, player in self.context.current_game.players.items():
                    if player.current_answer is None:
                        # Player didn't answer, assign -1 point
                        player.score -= 1
                        total_points_lost += 1
                        player.nums_of_wrong_answers += 1
                    else:
                        # Player answered
                        if player.current_answer == correct_answer:
                            print("Player answered correctly.")
                            print("Player:", player.name)
                            # Correct answer
                            if player.answer_time < fastest_time:
                                fastest_player = player
                                fastest_time = player.answer_time

                            player.nums_of_wrong_answers = 0
                            player.score += 1
                        else:
                            print("Player answered incorrectly.")
                            print("Player:", player.name)

                            # Wrong answer
                            player.score -= 1
                            total_points_lost += 1
                            player.nums_of_wrong_answers += 1

                        # Check for disqualification
                        if player.nums_of_wrong_answers == 3:
                            disqualified_players.append(player)

                # Disqualify players
                for disqualified_player in disqualified_players:
                    # Broadcast to the disqualified player
                    disqualified_player.client_socket.send(DisqualifiedMessage().pack())

                    del self.context.current_game.players[disqualified_player.client_address]

                # Update score for fastest player
                for player in self.context.current_game.players.values():
                    if player == fastest_player:
                        player.score += total_points_lost

                # Update positions
                for player in self.context.current_game.players.values():
                    player.position += player.score
                    if player.position < 1:
                        player.position = 1

                # Announce results
                for address, player in self.context.current_game.players.items():
                    is_correct = player.current_answer == correct_answer
                    result_message = ResultMessage(correct_answer, is_correct, player.position)
                    player.client_socket.send(result_message.pack())

                    print("Sent result message:", result_message.__dict__)
                    print("To player:", player.name)
                
                # Check if all players are disqualified
                if len(self.context.current_game.players) == 0:
                    # End the game
                    self.context.transition_to(WaitingState())
                    self.context.current_game = None

                    return

                # Check for winner
                if any(player.position >= self.context.current_game.race_length for player in self.context.current_game.players.values()):
                    # Announce winner
                    winner = max(self.context.current_game.players.values(), key=lambda x: x.position)
                    
                    print("Winner:", winner.name)
                    # Broadcast the winner message to all players
                    for address, player in self.context.players.items():
                        player.client_socket.send(WinnerMessage(winner.name).pack())
                    
                    # End the game
                    self.context.transition_to(WaitingState())
                    self.context.current_game = None
                else:
                    # Start next round
                    self.context.current_game.remaining_time = -1

    def handle_disconnect(self, data_pack) -> None:
        client_address = data_pack[2]
        if client_address in self.context.players:
            del self.context.players[client_address]
        
        if client_address in self.context.current_game.players:
            del self.context.current_game.players[client_address]

        # # Broadcast the player disconnected message to all players
        # for address, player in self.context.players.items():
        #     player.client_socket.send(PlayerDisconnectedMessage().pack())

        print("Player disconnected.")

        

# Define the server class
class GameServer:
    _state : State = None

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.players = {}  # Dictionary to store connected players
        self.message_queue = queue.Queue()  # Queue for inter-thread communication
        self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
        self.transition_to(WaitingState())
        self.current_game : Game = None

        self.message_handlers = {
            MessageType.JOIN: self.request_join,
            MessageType.READY: self.request_ready,
            MessageType.TICK: self.request_tick,
            MessageType.ANSWER: self.request_answer,
            MessageType.DISCONNECT: self.request_disconnect,
        }
    
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
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()

    def handle_client(self, client_socket, client_address):
        # Receive messages from the client and put them into the message queue
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                # Put received message into the queue
                self.message_queue.put([data, client_socket, client_address])
            except Exception as e:
                print("Error receiving message:", e)
                break
        
        # Close the client socket
        self.message_queue.put([DisconnectMessage().pack(), client_socket, client_address])

    def timer_loop(self):
        # Timer loop to send 'tick' message into the queue
        while True:
            self.message_queue.put([TickMessage().pack(), None, None])
            time.sleep(1)

    def process_messages(self):
        # Process messages from the queue and handle server logic based on the current state
        while True:
            # try:
                data_pack = self.message_queue.get()
                message = Message.unpack(data_pack[0])
                
                if message.type in self.message_handlers:
                    if message.type != MessageType.TICK:
                        print("Message:", message.__dict__)
                    self.message_handlers[message.type](data_pack)
                else:
                    print("Unhandled message type:", message.type)


            # except Exception as e:
            #     print("Error processing message:", e)
            #     continue
    
    def request_join(self, data_pack):
        self._state.handle_join(data_pack)
    
    def request_tick(self, data_pack):
        self._state.handle_tick(data_pack)

    def request_ready(self, data_pack):
        self._state.handle_ready(data_pack)
    
    def request_answer(self, data_pack):
        self._state.handle_answer(data_pack)
    
    def request_disconnect(self, data_pack):
        self._state.handle_disconnect(data_pack)

if __name__ == "__main__":
    server = GameServer(HOST, PORT)
    
    server.start()
