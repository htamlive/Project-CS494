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
            
        self.players = None
        
        
        self.request_current_players_in_room()

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

        self.init_leave_waiting_room_popup()

        def on_ready():
            self.is_ready = True
            self.game.proxy.on_ready()
            ready_button.set_enabled(False, False)


        def on_leave():
            self.game.show_popup('leave waiting room')

        ready_button.on_click = on_ready
        leave_button.on_click = on_leave


        self.buttons.extend([ready_button,leave_button])

        

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
        if(self.game.proxy.is_game_started()):
            self.game.push_state(GamePlayState(self.game, self.game.proxy.get_mode()))
            
    def request_current_players_in_room(self):
        # players = self.get_current_players()
        # if players != Socket_return.IS_WAITING:
        #     self.players = players

        pass
        
        return self.game.proxy.get_current_players()
    
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
            arcade.draw_text("Waiting for other players...", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 
                         arcade.color.BLACK, 12, font_name=self.font,align='center',width=300)
        else:
            arcade.draw_text("Press Ready when you're ready", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 
                         arcade.color.BLACK, 12, font_name=self.font,align='center',width=300)
            
        no_of_players = self.get_number_of_players()
        no_of_ready_players = self.get_number_of_ready_players()

        arcade.draw_text(f"{no_of_ready_players}/{no_of_players} ready", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 90, 
                         arcade.color.BLACK, 20, font_name=self.font,align='center',width=300)
        
        
        # for idx, player in enumerate(self.players):
        #     arcade.draw_text(player, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 80 - idx * 40, 
        #                      arcade.color.BLACK, 20, font_name=self.font)