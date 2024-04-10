from __future__ import annotations
from message import *

from ..player import Player
from ..message_data import MessageData
from ..config import *
from .server_state import State
from . import starting_state


class WaitingState(State):
    def handle(self, data_pack) -> None:
        match data_pack:
            case MessageData(JoinMessage(room, name), client_socket, client_address):
                self._handle_join(
                    JoinMessage(room, name), client_socket, client_address
                )
            case MessageData(ReadyMessage(state), client_socket, client_address):
                self._handle_ready(ReadyMessage(state), client_address)
            case MessageData(DisconnectMessage(), client_socket, client_address):
                self._handle_disconnect(client_address)

    def _handle_join(self, message: JoinMessage, client_socket, client_address) -> None:
        print("Join message:", repr(message))

        player_name = message.name
        if (
            client_address in self.context.players
            or len(self.context.players) == MAX_PLAYERS
            or any(
                player.name == player_name for player in self.context.players.values()
            )
        ):
            client_socket.send(JoinDenyMessage().pack())
            return

        print("Player joined:", player_name)
        self.context.players[client_address] = Player(
            player_name, client_socket, client_address
        )
        client_socket.send(JoinAckMessage().pack())

    def _handle_ready(self, message: ReadyMessage, client_address) -> None:
        if not message.state:
            return
        # Check if the player is already in the players dictionary
        if client_address not in self.context.players:
            return

        # Check if the player is already ready
        player = self.context.players[client_address]
        if player.ready:
            return

        player.ready = True

        # Get number of ready players
        ready_players = sum(
            1 for player in self.context.players.values() if player.ready
        )

        # Broadcast the ready message to all players
        for address, player in self.context.players.items():
            player.client_socket.send(ReadyChangeMessage(ready_players).pack())

        # Check if all players are ready
        if ready_players == len(self.context.players):
            # Broadcast the start game message to all players
            for address, player in self.context.players.items():
                player.client_socket.send(StartGameMessage(RACE_LENGTH).pack())

            # Start the game
            self.context.transition_to(starting_state.StartingState())

            print("Game started!")

    def _handle_disconnect(self, client_address) -> None:
        if client_address in self.context.players:
            del self.context.players[client_address]

        # Broadcast the player disconnected message to all players
        for address, player in self.context.players.items():
            player_count = len(self.context.players)
            player.client_socket.send(PlayersChangedMessage(player_count).pack())

        print("Player disconnected.")
