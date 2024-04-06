import arcade
from .state import State
from .waiting_room_state import WaitingRoomState
from ..buttons import HoverLineButton
from ..alert_notification import InputPopup, OKNotification
from config.config import *


class ChooseModeState(State):
    def __init__(self, game):
        super().__init__(game)
        
        self.mode_title = arcade.load_texture("resources/images/titleMode.png")


        traditional_button = HoverLineButton("resources/images/btnTraditional.png", 0.5)
        traditional_button.click_scale_factor = 0.6
        traditional_button.center_x = SCREEN_WIDTH // 2
        traditional_button.center_y = SCREEN_HEIGHT // 2 - 20 + 50


        blitz_button = HoverLineButton("resources/images/btnBlitz.png", 0.5)
        blitz_button.click_scale_factor = 0.6
        blitz_button.center_x = SCREEN_WIDTH // 2
        blitz_button.center_y = SCREEN_HEIGHT // 2 - 120 + 50

        self.mode = Mode.TRADITIONAL

        traditional_button.on_click = lambda : self.set_mode(Mode.TRADITIONAL)
        blitz_button.on_click = lambda : self.set_mode(Mode.BLITZ)

        self.buttons.extend([traditional_button, blitz_button])

        self.init_result_box()


        def on_ok():
            current_text = self.input_popup.get_current_text()
            if self.register_with_name(current_text):
                self.input_popup.show_noti("Valid name", arcade.color.GREEN)
                self.game.turn_off_notification('input name')


                self.game.show_popup('Registration notification')
                
            else:
                self.input_popup.show_noti("Invalid name", arcade.color.RED)

        def on_cancel():
            self.game.turn_off_notification('input name')
            self.game.pop_state()

        self.input_popup = InputPopup("Enter your name", on_ok = on_ok, on_cancel= on_cancel)

        self.game.popups['input name'] = self.input_popup

    def init_result_box(self):
        def on_ok():
            self.game.push_state(WaitingRoomState(self.game, self.mode))
            self.game.turn_off_notification('Registration notification')

        self.ok_notification =  OKNotification("Registration Completed Successfully", on_ok = on_ok)

        self.game.popups['Registration notification'] = self.ok_notification
        
    def set_mode(self, mode):
        self.game.show_popup('input name')
        self.mode = mode
        
    
    def register_with_name(self, name):
        return self.game.proxy.register(name, self.mode)
    
    def renew_input_box(self):
        self.ui_manager.remove(self.input_box)
        self.input_box = self.init_input_box()
        self.ui_manager.add(self.input_box)

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)

        self.ui_manager.on_key_press(symbol, modifiers)

        if(self.input_box.text == ''):
            self.renew_input_box()
            self.input_box._active = True


    def draw(self):
        super().draw()
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 + 160, 
                                             self.mode_title, 0.35)