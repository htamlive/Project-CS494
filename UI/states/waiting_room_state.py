import arcade
from .state import State
from .game_play_state import GamePlayState
from ..buttons import ImageButton, HoverLineButton
from ..alert_notification import OKNotification, AlertNotification
from config.config import *


class WaitingRoomState(State):
    def __init__(self, game, mode):
        super().__init__(game)
        
        
        self.player_title = arcade.load_texture("resources/images/playersTitle.png")

        self.mode_label = arcade.load_texture("resources/images/traditionalModeLabel.png")

        if(mode == Mode.BLITZ):
            self.mode_label = arcade.load_texture("resources/images/blitzModeLabel.png")

        # traditional_button = HoverLineButton("resources/images/btnTraditional.png", 0.5)
        # traditional_button.click_scale_factor = 0.6
        # traditional_button.center_x = SCREEN_WIDTH // 2
        # traditional_button.center_y = SCREEN_HEIGHT // 2 - 20
        # self.buttons.extend([traditional_button, blitz_button])
            
        arcade.load_font("resources/fonts/PaytoneOne-Regular.ttf")

        self.font = "Paytone One"
            
        self.players = []
        
        self.request_current_players_in_room()

        self.is_ready = False

        self.current_page = 0
        self.player_per_page = 4

        # start_button = ImageButton("resources/images/btnStart.png", 0.4)
        # start_button.click_scale_factor = 0.5
        # start_button.center_x = SCREEN_WIDTH // 2
        # start_button.center_y = SCREEN_HEIGHT // 2 - 235

        # start_button.on_click = lambda : self.game.push_state(GamePlayState(self.game, mode))

        
        left_arrow_button = HoverLineButton("resources/images/leftArrow.png", 0.2)
        left_arrow_button.click_scale_factor = 0.3
        left_arrow_button.center_x = SCREEN_WIDTH//2 - 40
        left_arrow_button.center_y = SCREEN_HEIGHT//2 - 80 - 90
        left_arrow_button.hovered_line_speed = 5

        right_arrow_button = HoverLineButton("resources/images/rightArrow.png", 0.2)
        right_arrow_button.click_scale_factor = 0.3
        right_arrow_button.center_x = SCREEN_WIDTH//2 + 40
        right_arrow_button.center_y = SCREEN_HEIGHT//2 - 80 - 90
        right_arrow_button.hovered_line_speed = 5

        def on_left_arrow():
            if self.current_page > 0:
                self.current_page -= 1

        def on_right_arrow():
            
            if (self.current_page + 1)*self.player_per_page< len(self.players):
                self.current_page += 1

        left_arrow_button.on_click = on_left_arrow
        right_arrow_button.on_click = on_right_arrow


        leave_button = HoverLineButton("resources/images/btnLeave.png", 0.8, line_color=arcade.color.RED)
        leave_button.click_scale_factor = 0.9
        leave_button.center_x = SCREEN_WIDTH // 2 + 150
        leave_button.center_y = SCREEN_HEIGHT // 2 + 160

        ready_button = ImageButton("resources/images/btnReady.png", 0.5)
        ready_button.click_scale_factor = 0.6
        ready_button.center_x = SCREEN_WIDTH // 2
        ready_button.center_y = SCREEN_HEIGHT // 2 - 230

        self.init_leave_waiting_room_popup()

        def on_ready():
            self.is_ready = True
            self.game.proxy.on_ready()
            ready_button.set_enabled(False, False)


        def on_leave():
            self.game.show_popup('leave waiting room')

        ready_button.on_click = on_ready
        leave_button.on_click = on_leave


        self.buttons.extend([ready_button,leave_button, left_arrow_button, right_arrow_button])

        

    def init_leave_waiting_room_popup(self):
        def on_ok():
            self.game.proxy.leave_game()
            self.game.return_menu()
            self.game.turn_off_notification('leave waiting room')
        
        def on_cancel():
            self.game.turn_off_notification('leave waiting room')
        
        self.leave_waiting_room_popup = AlertNotification("Are you sure you want to leave?", on_ok, on_cancel)
        self.game.popups['leave waiting room'] = self.leave_waiting_room_popup

    def on_update(self, delta_time):
        super().on_update(delta_time)
        self.request_current_players_in_room()
        if(self.game.proxy.is_game_started()):
            self.game.push_state(GamePlayState(self.game, self.game.proxy.get_mode()))

        if(len(self.players) == 0):
            self.buttons[-1].set_enabled(False, False)
            self.buttons[-2].set_enabled(False, False)
        else:
            enable_left = self.current_page > 0
            enable_right = (self.current_page + 1) * self.player_per_page < len(self.players)
            self.buttons[-2].set_enabled(enable_left, enable_left)
            self.buttons[-1].set_enabled(enable_right, enable_right)

            
    def request_current_players_in_room(self):
        players = self.game.proxy.get_current_players()
        if players != Socket_return.IS_WAITING:
            if(self.check_diff_players(players)):
                self.current_page = 0
                self.players = players

    def check_diff_players(self, players):

        if len(self.players) != len(players):
            return True
        for i in range(len(players)):
            if self.players[i][0] != players[i][0] or self.players[i][1] != players[i][1]:
                return True
        return False
    
    def get_number_of_players(self):
        return self.game.proxy.get_number_of_players()
    
    def get_number_of_ready_players(self):
        return self.game.proxy.get_number_of_ready_players()


    def draw(self):
        super().draw()
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 + 150, 
                                             self.player_title, 0.75)
        
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT//2 + 120, 
                                             self.mode_label, 0.5)
        

        if(self.is_ready):
            arcade.draw_text("Waiting for other players...", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 40, 
                         arcade.color.BLACK, 12, font_name=self.font,align='center',width=300)
        else:
            arcade.draw_text("Press Ready when you're ready", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 40, 
                         arcade.color.BLACK, 12, font_name=self.font,align='center',width=300)
            
        no_of_players = self.get_number_of_players()
        no_of_ready_players = self.get_number_of_ready_players()

        arcade.draw_text(f"{no_of_ready_players}/{no_of_players} ready", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 90, 
                         arcade.color.BLACK, 20, font_name=self.font,align='center',width=300)
        
        
        for idx, (player_name, is_ready) in enumerate(self.players[self.current_page * self.player_per_page: (self.current_page + 1) * self.player_per_page]):
            color = arcade.color.LIME_GREEN if is_ready else arcade.color.BLACK
            arcade.draw_text(player_name, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 5 - idx * 40, 
                             color, 20, font_name=self.font, align='center', width=200)