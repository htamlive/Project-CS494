import random
from message import *
from .config import NUMS_OF_QUESTIONS


class Game:
    def __init__(self, race_length):
        self.race_length = race_length
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
