import arcade
from .state import State
from .game_play_state import GamePlayState
from ..buttons import ImageButton, HoverLineButton
from ..alert_notification import OKNotification
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
            
        self.font = arcade.load_font("resources/fonts/PaytoneOne-Regular.ttf")
            
        self.players = self.get_current_players()

        self.is_ready = False

        # start_button = ImageButton("resources/images/btnStart.png", 0.4)
        # start_button.click_scale_factor = 0.5
        # start_button.center_x = SCREEN_WIDTH // 2
        # start_button.center_y = SCREEN_HEIGHT // 2 - 235

        # start_button.on_click = lambda : self.game.push_state(GamePlayState(self.game, mode))

        leave_button = HoverLineButton("resources/images/btnLeave.png", 0.8, line_color=arcade.color.RED)
        leave_button.click_scale_factor = 0.9
        leave_button.center_x = SCREEN_WIDTH // 2 + 150
        leave_button.center_y = SCREEN_HEIGHT // 2 + 160

        ready_button = ImageButton("resources/images/btnReady.png", 0.5)
        ready_button.click_scale_factor = 0.6
        ready_button.center_x = SCREEN_WIDTH // 2
        ready_button.center_y = SCREEN_HEIGHT // 2 - 230

        def on_ready():
            self.is_ready = True
            self.game.proxy.on_ready()
            ready_button.set_enabled(False, False)


        def on_leave():
            self.game.proxy.leave_game()
            self.game.return_menu()


        ready_button.on_click = on_ready
        leave_button.on_click = on_leave


        self.buttons.extend([ready_button,leave_button])

    def on_update(self, delta_time):
        super().on_update(delta_time)
        if(self.game.proxy.is_game_started()):
            self.game.push_state(GamePlayState(self.game, self.game.proxy.get_mode()))

            

            
    def get_current_players(self):
        return self.game.proxy.get_current_players()


    def draw(self):
        super().draw()
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 + 150, 
                                             self.player_title, 0.75)
        
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT//2 + 120, 
                                             self.mode_label, 0.5)
        

        if(self.is_ready):
            arcade.draw_text("Waiting for other players...", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 230, 
                         arcade.color.BLACK, 12, font_name=self.font,align='center',width=300)
        
        for idx, player in enumerate(self.players):
            arcade.draw_text(player, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 80 - idx * 40, 
                             arcade.color.BLACK, 20, font_name=self.font)