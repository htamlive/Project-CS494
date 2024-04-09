import logging
from client import Client

if __name__ == "__main__":
    logging.basicConfig(format='[%(levelname)s]  %(message)s', level=logging.DEBUG)
    client = Client("localhost", 4001)

    name = input("Enter your name: ")
    client.register(name, "normal")

    ready = input("Are you ready? (y/n): ")
    while ready != "y":
        ready = input("Are you ready? (y/n): ")

    client.on_ready()

    while not client.is_game_started():
        pass

    print("Game started!")
    while True:
        operand1, operator, operand2, _ = client.gen_quest()
        print(f"Question: {operand1} {operator} {operand2}")
        answer = int(input("Your answer: "))
        client.check_answer(answer, None)
