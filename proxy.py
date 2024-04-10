import random
from config.config import *

class Proxy:
    '''
        + register
        + ready (checked)
        + game started
        + send answer
        + request new question
    '''
    def __init__(self):
        # connect to the server

        '''
        The following is the template for the functions that you need to implement

        You can add more variables and functions if you need to. This can help you store some useful information
        '''

        self.time_left = DEFAULT_TIME
        self.dummy_test_time = 0
        self.current_mode = None

        self.score = 0

        self.result = None

    def on_update(self, delta_time):
        '''
        This function is called every frame
        '''
        self.dummy_test_time += delta_time

    def register(self, name, mode):
        '''
        If correct, please register the user to the game
        The player will be in ready state
        '''
        self.current_mode = mode
        return True
    
    def get_current_players(self):
        '''
        return the list of current players
        '''
        return ['Player 1', 'Player 2', 'Player 3']
    
    def is_game_started(self):
        '''
        If the room is full, the game will be started
        return True if the game is started. Otherwise, return False
        '''
        return self.dummy_test_time > 10
    
    def on_ready(self):
        '''
        The player is ready to play the game
        '''
        pass
    
    def get_mode(self):
        '''
        return the mode of the game
        '''
        return self.current_mode
    
    def leave_game(self):
        '''
        leave the game
        This function is used when the user clicks the leave button in waiting room or game play state
        '''
        pass
    
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
    
    def submit_answer(self, answer, stored_server_answer):
        '''
        you may retrieve the answer from the server instead of the stored_server_answer


        New version: just update the local result of proxy, does not need to return anything
        '''
        # result = Result.INCORRECT
        # try:
        #     user_input = int(answer)
        #     if user_input == stored_server_answer:
        #         result = Result.CORRECT
        #     else:
        #         result = Result.INCORRECT
        # except:
        #     result = Result.INCORRECT

        # self.result = result

        pass

    
    '''
    TODO
    '''
    def get_racing_length(self):
        return 100

    def get_user_top(self):
        return 1
    
    def get_user_score(self, stored_score):
        '''
        You dont need to use the stored score. Just let it to match the calling
        '''
        return stored_score
    
    def update_time_left(self, dt):
        '''
        update the time left
        This will update frame by frame. The return value will be used to check if the game is over
        Return False if game over. Otherwise, return True
        '''
        
        self.time_left -= dt
        
        if self.time_left <= 0:
            return False
        return True
    
    def get_time_left(self):
        return self.time_left

    def init_time(self):
        '''
        Initialize the time for the user when the game starts
        '''
        self.time_left = DEFAULT_TIME
        return DEFAULT_TIME
    
    def get_current_players_with_scores(self):
        '''
        Sort in-order of score
        '''
        return [
            ('Player 1', 4),
            ('Player 2', 2),
            ('Player 3', 1),
        ]
    
    def get_number_of_players(self):
        return 3
    
    def get_number_of_ready_players(self):
        return 3
    
    def get_number_of_players_in_game(self):
        return 3
    
    def get_winner(self):
        '''
        Use for lost players

        + None
        + Player 1

        '''
        return 'Player 1'
    
    def check_result(self):
        '''
        This function will ask for every frame if the server is timeout

        This function will update score

        return the result, which is the enum of Result if the server approves the UI to update and show the result and the score
        Otherwise, return None

        Return None, None

        correct
        incorrect

        Leaderboard
        Your score: 1/100

        Player 1

        self.score = ...
        self.winner = ...

        '''
        result = self.result
        self.result = None
        return result
    

        
