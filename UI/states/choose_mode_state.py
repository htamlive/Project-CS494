import arcade
from .state import State
from .waiting_room_state import WaitingRoomState
from ..buttons import HoverLineButton
from config.config import *


class ChooseModeState(State):
    def __init__(self, game):
        super().__init__(game)
        
        self.mode_title = arcade.load_texture("resources/images/titleMode.png")


        traditional_button = HoverLineButton("resources/images/btnTraditional.png", 0.5)
        traditional_button.click_scale_factor = 0.6
        traditional_button.center_x = SCREEN_WIDTH // 2
        traditional_button.center_y = SCREEN_HEIGHT // 2 - 20


        blitz_button = HoverLineButton("resources/images/btnBlitz.png", 0.5)
        blitz_button.click_scale_factor = 0.6
        blitz_button.center_x = SCREEN_WIDTH // 2
        blitz_button.center_y = SCREEN_HEIGHT // 2 - 120

        traditional_button.on_click = lambda : self.game.push_state(WaitingRoomState(game, Mode.TRADTIONAL))
        blitz_button.on_click = lambda : self.game.push_state(WaitingRoomState(game, Mode.BLITZ))

        self.buttons.extend([traditional_button, blitz_button])


    def draw(self):
        super().draw()
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 + 90, 
                                             self.mode_title, 0.5)