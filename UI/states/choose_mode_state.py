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


        self.init_pop_up_box()

        traditional_button.on_click = lambda : self.set_mode(Mode.TRADITIONAL)
        # blitz_button.on_click = lambda : self.set_mode(Mode.BLITZ)
        blitz_button.on_click = lambda : self.game.show_popup('blitz notification')

        self.buttons.extend([traditional_button, blitz_button])

        


        def on_ok():
            current_text = self.input_popup.get_current_text()
            if current_text == '':
                self.input_popup.show_noti("Name cannot be empty", arcade.color.RED)
                return
            
            # can contains _ and numbers
            valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
            if len(current_text) > 10 or any([c not in valid_chars for c in current_text]):
                self.input_popup.show_noti("Invalid name", arcade.color.RED)
                return
            
            def query_func():
                current_text = self.input_popup.get_current_text()


                ret = self.register_with_name(current_text)

                if ret != Socket_return.IS_WAITING:
                    if ret:
                        self.input_popup.show_noti("Valid name", arcade.color.GREEN)
                        self.game.turn_off_notification('input name')


                        self.game.show_popup('Registration notification')
                        
                    else:
                        self.input_popup.show_noti("Invalid name", arcade.color.RED)
                    return True
                return False
            
            self.game.waiting_notification.add_query(query_func)


        def on_cancel():
            self.game.turn_off_notification('input name')
            self.game.pop_state()

        self.input_popup = InputPopup("Enter your name", on_ok = on_ok, on_cancel= on_cancel)

        self.game.popups['input name'] = self.input_popup

    def init_pop_up_box(self):

        self.blitz_notification = OKNotification("Blitz mode is not available yet", on_ok = lambda: self.game.turn_off_notification('blitz notification'))

        self.game.popups['blitz notification'] = self.blitz_notification
        
    
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
    


    def draw(self):
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 + 160, 
                                             self.mode_title, 0.35)
        super().draw()

    def on_update(self, delta_time):
        super().on_update(delta_time)
