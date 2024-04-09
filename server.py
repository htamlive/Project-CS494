from server.server import GameServer

if __name__ == '__main__':
    server = GameServer("localhost", 4001)

    server.start()
