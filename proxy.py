import random
from config.config import *

class Proxy:
    def __init__(self):
        # connect to the server

        '''
        The following is the template for the functions that you need to implement

        You can add more variables and functions if you need to. This can help you store some useful information
        '''

        pass

    def on_update(self, delta_time):
        '''
        This function is called every frame
        '''
        pass

    def check_valid_name(self, name):
        '''
        If correct, please register the user to the game
        '''
        return True
    
    def gen_quest(self):

        operand1 = random.randint(1, 100)
        operand2 = random.randint(1, 100)
        operator = random.choice(list(Operator))
        if operator == Operator.ADD:
            result = operand1 + operand2
        elif operator == Operator.SUBTRACT:
            result = operand1 - operand2
        elif operator == Operator.MULTIPLY:
            result = operand1 * operand2
        elif operator == Operator.DIVIDE:
            result = operand1 // operand2
        elif operator == Operator.MOD:
            result = operand1 % operand2

        print(operand1, operator, operand2, result)

        return operand1, operator, operand2, result
    
    def check_answer(self, answer, stored_server_answer):
        '''
        you may retrieve the answer from the server instead of the stored_server_answer
        '''
        result = Result.INCORRECT
        try:
            user_input = int(answer)
            if user_input == stored_server_answer:
                result = Result.CORRECT
            else:
                result = Result.INCORRECT
        except:
            result = Result.INCORRECT

        return result
    
    def get_score(self):
        '''
        return the score of the quest if the user answers correctly. Otherwise, return 0
        '''
        return 1

    def get_user_top(self):
        return 1
    
    def get_user_score(self, stored_score):
        '''
        You dont need to use the stored score. Just let it to match the calling
        '''
        return stored_score