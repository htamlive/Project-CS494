from __future__ import annotations
from message import *

from ..game import Game
from ..message_data import MessageData
from ..config import *

from .server_state import State
from . import waiting_state

import time

class StartingState(State):
    def handle(self, data_pack) -> None:
        match data_pack:
            case MessageData(AnswerMessage(answer), _, client_address):
                self._handle_answer(AnswerMessage(answer), client_address)
            case TickMessage():
                self._handle_tick()
            case MessageData(DisconnectMessage(), _, client_address):
                self._handle_disconnect(client_address)

    def _handle_answer(self, message: AnswerMessage, client_address) -> None:
        if self.context.current_game is None:
            raise Exception("Game is not initialized.")
        if self.context.current_game.remaining_time == -1:
            return

        if client_address not in self.context.current_game.players:
            return

        answer = message.answer
        player = self.context.current_game.players[client_address]
        player.current_answer = answer
        player.answer_time = time.time_ns()

    def _find_winner(self):
        if self.context.current_game is None:
            raise Exception("Game is not initialized.")
        if any(
            player.position >= self.context.current_game.race_length
            for player in self.context.current_game.players.values()
        ):
            # Announce winner
            winner = max(
                self.context.current_game.players.values(),
                key=lambda x: x.position,
            )
            return winner
        return None

    def _start_new_round(self):
        if self.context.current_game is None:
            raise ValueError("Game is not initialized.")

        self.context.current_game.current_index += 1

        # Reset answers
        for player in self.context.current_game.players.values():
            player.current_answer = None
            player.answer_time = None

        # Broadcast the question to all players
        for address, player in self.context.current_game.players.items():
            player.client_socket.send(
                self.context.current_game.question[
                    self.context.current_game.current_index
                ].pack()
            )
            print(
                "Sent question:",
                repr(
                    self.context.current_game.question[
                        self.context.current_game.current_index
                    ]
                ),
            )

        self.context.current_game.remaining_time = QUESTION_TIME_LIMIT

    def _end_round(self):
        if self.context.current_game is None:
            raise ValueError("Game is not initialized.")

        # Broadcast the time out message to all players
        for address, player in self.context.current_game.players.items():
            player.client_socket.send(TimeOutMessage().pack())
            print("Sent time out message.")

        # Start checking the answers
        correct_index = self.context.current_game.current_index
        fastest_player = None
        fastest_time = float("inf")
        total_points_lost = 0
        disqualified_players = []

        # Calculate the correct answer and find the fastest player
        num1 = self.context.current_game.question[correct_index].first_number
        num2 = self.context.current_game.question[correct_index].second_number
        operation = self.context.current_game.question[correct_index].operation

        correct_answer: int
        match operation:
            case Operation.ADD:
                correct_answer = num1 + num2
            case Operation.SUB:
                correct_answer = num1 - num2
            case Operation.MUL:
                correct_answer = num1 * num2
            case Operation.DIV:
                correct_answer = num1 / num2
            case _:
                raise ValueError("Invalid operation.")

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
            self.context.transition_to(waiting_state.WaitingState())
            self.context.current_game = None

            return

        # Check for winner
        winner = self._find_winner()
        if winner is not None:
            print("Winner:", winner.name)
            # Broadcast the winner message to all players
            for address, player in self.context.players.items():
                print(WinnerMessage(winner.name).pack())
                print(player.client_socket.sendall(WinnerMessage(winner.name).pack()))

            # End the game
            self.context.transition_to(waiting_state.WaitingState())
            self.context.current_game = None
        else:
            # Start next round
            self.context.current_game.remaining_time = -1

    def _handle_tick(self):
        if self.context.current_game is None:
            # Create a new game
            self.context.current_game = Game(RACE_LENGTH, self.context.players)
            self.context.current_game.new_question_list()
            self.context.current_game.remaining_time = -1
            self.context.current_game.current_index = -1

            print("New game created.")

        if self.context.current_game.remaining_time == -1:
            # New question
            self._start_new_round()
        else:
            self.context.current_game.remaining_time -= 1

            if self.context.current_game.remaining_time == 0 or all(
                player.current_answer is not None
                for player in self.context.current_game.players.values()
            ):
                self._end_round()

    def _handle_disconnect(self, client_address) -> None:
        if self.context.current_game is None:
            raise Exception("Game is not initialized.")

        if client_address in self.context.players:
            del self.context.players[client_address]

        if client_address in self.context.current_game.players:
            del self.context.current_game.players[client_address]

        # # Broadcast the player disconnected message to all players
        # for address, player in self.context.players.items():
        #     player.client_socket.send(PlayerDisconnectedMessage().pack())

        print("Player disconnected.")
