from __future__ import annotations
from abc import ABC, abstractmethod
from message import *

from ..game import Game
from ..player import Player
from ..message_data import MessageData
from ..config import *
import server.server as sv

import time


class State(ABC):
    @property
    def context(self) -> sv.GameServer:
        return self._context

    @context.setter
    def context(self, context: sv.GameServer) -> None:
        self._context = context

    @abstractmethod
    def handle(self, data_pack) -> None:
        pass



