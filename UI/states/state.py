from arcade.gui import UIManager
import arcade

class State:
    def __init__(self, game):
        self.game = game
        self.buttons = arcade.sprite_list.SpriteList()

        self.ui_manager = UIManager()


    def is_notification_on(self):
        return False
        
    def on_mouse_motion(self, x, y, dx, dy):
        if(not self.is_notification_on()):
            for button in self.buttons:
                button.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        if(not self.is_notification_on()):
            for button in self.buttons:
                button.on_mouse_press(x, y, button, modifiers)

    def on_update(self, delta_time):

        if(not self.is_notification_on()):
            for button in self.buttons:
                button.on_update(delta_time)

            self.ui_manager.on_update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_key_release(self, symbol: int, modifiers: int):
        pass

    def on_draw(self):
    
        for button in self.buttons:
            button.on_draw()


    def draw(self):
        self.buttons.draw()

        for button in self.buttons:
            button.draw_effect()
