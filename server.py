from server.server import GameServer
from config.config import *
if __name__ == '__main__':
    server = GameServer(SERVER_ADDR, 4001)

    server.start()
