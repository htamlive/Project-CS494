from .state import State
import arcade
from ..buttons import HoverLineButton, ImageButton
from .choose_mode_state import ChooseModeState
from .setting_state import SettingsState
from config.config import *
from ..alert_notification import AlertNotification, OKNotification

class MenuState(State):
    def __init__(self, game):
        super().__init__(game)

        # Play button
        play_button = HoverLineButton("resources/images/btnPlay.png", 1.0)
        play_button.center_x = SCREEN_WIDTH // 2
        play_button.center_y = SCREEN_HEIGHT // 2 + 50
        

        # Settings button
        settings_button = HoverLineButton("resources/images/btnSettings.png", 1.0)
        settings_button.center_x = SCREEN_WIDTH // 2
        settings_button.center_y = SCREEN_HEIGHT // 2 - 50
        

        # Quit button
        quit_button = HoverLineButton("resources/images/btnQuit.png", 1.0)
        quit_button.center_x = SCREEN_WIDTH // 2
        quit_button.center_y = SCREEN_HEIGHT // 2 - 150
        

        play_button.on_click = lambda : self.game.push_state(ChooseModeState(self.game))
        # settings_button.on_click = lambda : self.game.push_state(SettingsState(self.game))

        def on_ok():
            self.game.turn_off_notification('setting notification')


        self.ok_notification = OKNotification("Setting feature is not available yet", on_ok = on_ok)

        self.game.popups['setting notification'] = self.ok_notification


        settings_button.on_click = lambda : self.game.show_popup('setting notification')
        quit_button.on_click = lambda : arcade.close_window()

        self.buttons.extend([play_button, settings_button, quit_button])


    