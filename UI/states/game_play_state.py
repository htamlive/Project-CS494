import arcade
from arcade.gui import UIManager
from arcade.gui import UIInputText
from .state import State
from .summary_state import SummaryState
from ..buttons import ImageButton, HoverLineButton
from ..alert_notification import AlertNotification
from ..leaderboard import Leaderboard
from config.config import *
import random
from enum import Enum


class GamePlayState(State):
    def __init__(self, game, mode):
        super().__init__(game)

        self.history = []
        
        
        
        self.quest_title = arcade.load_texture("resources/images/questTitle.png")
        self.time_title = arcade.load_texture("resources/images/timeTitle.png")
        self.score_title = arcade.load_texture("resources/images/scoreTitle.png")
        


        self.submission_box = arcade.load_texture("resources/images/submissionBox.png")


        arcade.load_font("resources/fonts/PaytoneOne-Regular.ttf")

        self.font = "Paytone One"


        self.results = {
            Result.CORRECT: arcade.load_texture("resources/images/correctResult.png"),
            Result.INCORRECT: arcade.load_texture("resources/images/incorrectResult.png"),
        }

        self.result = None
        self.number_of_players = None
        self.current_score = self.game.proxy.get_user_score(None)
        self.timeleft = self.init_time()
        self.players_info = []

        self.request_racing_length()
        self.update_number_players()

        self.operators = {
            Operator.ADD: arcade.load_texture("resources/images/operators/addOperator.png"),
            Operator.SUBTRACT: arcade.load_texture("resources/images/operators/subtractOperator.png"),
            Operator.MULTIPLY: arcade.load_texture("resources/images/operators/multiplyOperator.png"),
            Operator.DIVIDE: arcade.load_texture("resources/images/operators/divideOperator.png"),
            Operator.MOD: arcade.load_texture("resources/images/operators/modOperator.png"),
        }

        

        self.ui_manager = UIManager()
        self.ui_manager.enable()
        self.input_box = self.init_input_box()

        self.ui_manager.add(self.input_box)

        
        self.mode = mode
        self.mode_label = arcade.load_texture("resources/images/traditionalModeLabel.png")

        if(mode == Mode.BLITZ):
            self.mode_label = arcade.load_texture("resources/images/blitzModeLabel.png")

        self.init_leave_game_popup()

        # traditional_button = HoverLineButton("resources/images/btnTraditional.png", 0.5)
        # traditional_button.click_scale_factor = 0.6
        # traditional_button.center_x = SCREEN_WIDTH // 2
        # traditional_button.center_y = SCREEN_HEIGHT // 2 - 20
        # self.buttons.extend([traditional_button, blitz_button])
            
            
        # self.players = self.get_current_players()

        self.go_button = ImageButton("resources/images/btnGo.png", 0.7)
        self.go_button.click_scale_factor = 0.8
        self.go_button.center_x = SCREEN_WIDTH // 2
        self.go_button.center_y = SCREEN_HEIGHT // 2 - 235

        self.go_button.on_click = lambda : self.on_submit()

        self.next_button = ImageButton("resources/images/btnNext.png", 0.7)
        self.next_button.click_scale_factor = 0.8
        self.next_button.center_x = SCREEN_WIDTH // 2
        self.next_button.center_y = SCREEN_HEIGHT // 2 - 230 - 2
        self.next_button.set_enabled(False, False)
        
        self.next_button.on_click = lambda : self.on_next_quest()
        

        leave_button = HoverLineButton("resources/images/btnLeave.png", 0.8, line_color=arcade.color.RED)
        leave_button.click_scale_factor = 0.9
        leave_button.center_x = SCREEN_WIDTH // 2 + 150
        leave_button.center_y = SCREEN_HEIGHT // 2 + 160

        
        leave_button.on_click = lambda : self.game.show_popup('leave game room')
        

        self.next_button.set_enabled(False, False)

        self.leaderboard = Leaderboard(self.game.proxy)

        self.buttons.extend([self.go_button, leave_button, self.next_button])
        self.buttons.extend(self.leaderboard.buttons)

        self.request_next_quest()


    def init_input_box(self):
        return UIInputText(
            x = SCREEN_WIDTH // 2 - 120,
            y = SCREEN_HEIGHT // 2 - 140,
            width = 200,
            height = 50,
            font_name = self.font,
            font_size = 20,
            text=''
        )
    
    def request_racing_length(self):

        self.racing_length = None

        def query_func():
            ret = self.game.proxy.request_racing_length()
            if ret != Socket_return.IS_WAITING:
                self.racing_length = ret
                self.leaderboard.racing_length = ret
                return True
            return False
        
        self.game.waiting_notification.add_query(query_func)
    
    def renew_input_box(self):
        self.ui_manager.remove(self.input_box)
        self.input_box = self.init_input_box()
        self.ui_manager.add(self.input_box)

    def init_time(self):
        initial_time = self.game.proxy.init_time()
        return initial_time

    
    def update_time(self, dt):
        still_have_time = self.game.proxy.update_time_left(dt)
        if not still_have_time:
            self.on_submit()

    def gen_quest(self):
        return self.game.proxy.gen_quest()

    def on_submit(self):
        user_input = self.input_box.text
        operand1, operator, operand2, result = self.history[-1]

        if(user_input == ''):
            user_input = '0'

        self.game.proxy.submit_answer(user_input, result)


        # self.go_button.set_enabled(False, False)

        def query_func_winner():
            winner = self.game.proxy.check_winner()
            if winner != Socket_return.IS_WAITING:
                if winner != None:
                    self.game.push_state(SummaryState(self.game, self.mode, self.current_score, Summary_type.WINNER, winner))
                else:
                    self.request_next_quest()
                return True
            return False


        def query_func():
        
            result = self.game.proxy.check_result()

            if(result != Socket_return.IS_WAITING):

                if(result == Result.DISQUALIFIED):
                    self.game.push_state(SummaryState(self.game, self.mode, self.current_score, type_of_summary=Summary_type.DISQUALIFIED))
                elif(result is not None):
                    self.result = result
                    self.update_score()
                    self.game.waiting_notification.add_query(query_func_winner)
                    
                    # self.next_button.set_enabled(True, True)

                return True

            return False
        
        self.game.waiting_notification.add_query(query_func)

    

    def update_score(self):
        self.current_score = self.game.proxy.get_user_score(None)

    def request_next_quest(self):
        def query_func():
            ret = self.gen_quest()
            if ret != Socket_return.IS_WAITING:
            
                self.history.append(ret)
                self.result = None
                self.next_button.set_enabled(False, False)
                self.renew_input_box()
                # self.go_button.set_enabled(True, True)
                # self.next_button.set_enabled(False, False)
                return True
            
            return False

        self.game.waiting_notification.add_query(query_func)

    def on_next_quest(self):
        if(self.next_button.is_enabled and self.next_button.visible):
            self.request_next_quest()
            

        
    def format_number(self, number : int) -> str:
        # format number with commas
        return "{:,}".format(number)
    
    def format_time(self, time : float) -> str:
        # format time to mm:ss
        rounded_time = round(time)
        minutes = rounded_time // 60
        seconds = rounded_time % 60
        return f"{minutes:02}:{seconds:02}"
    
    def draw_quest(self):

        if(len(self.history) == 0):
            return
        operand1, operator, operand2, _ = self.history[-1]

        texture_operator = self.operators[operator]

        for idx, operand in enumerate([operand1, operand2]):
            formatted_operand = self.format_number(operand)
            arcade.draw_text(formatted_operand, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 80 - idx * 130, 
                             arcade.color.BLACK, 28, font_name=self.font, align="center", width=100)
            
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30, 
                                             texture_operator, scale=0.8)
            
    def draw(self):
        super().draw()
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 + 150, 
                                             self.quest_title, 0.75)
        
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT//2 + 120, 
                                             self.mode_label, 0.5)
        
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH - 140, SCREEN_HEIGHT//2 + 180,
                                                self.score_title, 0.3)
        
        
        arcade.draw_scaled_texture_rectangle(150, SCREEN_HEIGHT//2 + 200,
                                                self.time_title, 0.5)
        
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 - 110 - 3,
                                                self.submission_box)
        

        # Draw the operands
        self.draw_quest()

        self.ui_manager.draw()

        self.leaderboard.draw()

        if(self.result):
            arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80, 
                                                 self.results[self.result], 0.7)
        
        arcade.draw_text(f'{str(self.current_score)}/{self.racing_length}', SCREEN_WIDTH - 200 + 10, SCREEN_HEIGHT//2 + 120 + 10, 
                             arcade.color.BLACK, 20, font_name=self.font, align="center", width=100)
        
        arcade.draw_text(self.format_time(self.timeleft), 95, SCREEN_HEIGHT//2 + 130, 
                             arcade.color.BLACK, 30, font_name=self.font, align="center", width=100)
        
        if(self.number_of_players is not None):
            arcade.draw_text(f"# players left", SCREEN_WIDTH - 200 - 20, SCREEN_HEIGHT - 80 - 20, arcade.color.BLACK, 16, font_name=self.font)
            arcade.draw_text(f"{self.number_of_players}", SCREEN_WIDTH - 60, SCREEN_HEIGHT - 80 -20, arcade.color.ORANGE_RED, 24, font_name=self.font)

        
        # for idx, player in enumerate(self.players):
        #     arcade.draw_text(player, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 80 - idx * 40, 
        #                      arcade.color.BLACK, 20, font_name=self.font)

    def init_leave_game_popup(self):
        def on_ok():
            self.game.proxy.leave_game()
            self.game.return_menu()
            self.game.turn_off_notification('leave game room')
        
        def on_cancel():
            self.game.turn_off_notification('leave game room')
        
        self.leave_waiting_room_popup = AlertNotification("Are you sure you want to leave?", on_ok, on_cancel)
        self.game.popups['leave game room'] = self.leave_waiting_room_popup


    def update_number_players(self):
        number_of_players = self.game.proxy.get_number_of_players_in_game()
        if number_of_players != Socket_return.IS_WAITING:
            self.number_of_players = number_of_players

    def on_update(self, delta_time):
        super().on_update(delta_time)
        self.update_time(delta_time)
        self.leaderboard.update(delta_time)
        self.update_number_players()
        self.timeleft = self.game.proxy.get_time_left()
        self.ui_manager.on_update(delta_time)


    def on_key_release(self, symbol: int, modifiers: int):
        self.ui_manager.on_key_release(symbol, modifiers)

    def on_draw(self):
        super().on_draw()
        self.ui_manager.on_draw()

        
    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(x, y, button, modifiers)
        self.ui_manager.on_mouse_press(x, y, button, modifiers)

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)

        self.ui_manager.on_key_press(symbol, modifiers)

        if(self.input_box.text == ''):
            self.renew_input_box()
            self.input_box._active = True


        
        
                


