import arcade
from UI.states.menu_state import MenuState
from config.config import *
from UI.alert_notification import WaitingNotification
from proxy import Proxy
from client import Client

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.WHITE)

        # Load the background image
        self.background = arcade.load_texture("resources/images/background.png")
        self.title = arcade.load_texture("resources/images/title.png")
        self.paper = arcade.load_texture("resources/images/paper.png")

        self.blue_wizard = arcade.load_texture("resources/images/blueWizard.png")
        self.white_wizard = arcade.load_texture("resources/images/whiteWizard.png")

        self.popups = dict()

        # Stack of states
        self.state_stack = []

        # Set initial state
        self.menu_state = MenuState(self)

        self.push_state(self.menu_state)

        self.proxy = Client('localhost', 4001)

        self.waiting_notification = WaitingNotification("Some magic is happening")

    def push_state(self, new_state):
        if(len(self.state_stack) > 0):
            for button in self.current_state.buttons:
                button.is_hover = False

        self.state_stack.append(new_state)

    def pop_state(self):
        if len(self.state_stack) > 1:
            self.state_stack.pop()
        
    
    def return_menu(self):
        while len(self.state_stack) > 1:
            self.state_stack.pop()


    @property
    def current_state(self):
        return self.state_stack[-1]
    
    def show_popup(self, name):
        self.popups[name].set_enabled(True)

    def on_draw(self):
        arcade.start_render()

        # Draw the background image
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        # Draw the title
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, 500, 90, self.title)

        # Draw the paper
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, 400, 500, self.paper)

        arcade.draw_scaled_texture_rectangle(120, SCREEN_HEIGHT // 2 + 20, self.blue_wizard, 0.5)

        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH - 150, 150, self.white_wizard, 0.5)


        if(self.current_state):
            self.current_state.draw()

        self.waiting_notification.draw()

        for box in self.popups.copy().values():
            box.draw()

    def turn_off_notification(self, name):
        self.popups[name].set_enabled(False)

    def remove_notification(self, name):
        self.popups[name].set_enabled(False)
        self.popups.pop(name)

    def is_notification_on(self):
        if(self.waiting_notification.enabled):
            return True
        
        for _, box in self.popups.items():
            if box.enabled:
                return True

    def on_mouse_motion(self, x, y, dx, dy):
        for _, box in self.popups.copy().items():
            box.on_mouse_motion(x, y, dx, dy)

        if(not self.is_notification_on()):
            self.current_state.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        for box in self.popups.copy().values():
            box.on_mouse_press(x, y, button, modifiers)

        if(not self.is_notification_on()):
            self.current_state.on_mouse_press(x, y, button, modifiers)

    def on_update(self, delta_time: float):

        self.proxy.on_update(delta_time)

        self.waiting_notification.on_update(delta_time)

        for box in self.popups.copy().values():
            box.on_update(delta_time)

        if(self.is_notification_on()):
            for button in self.current_state.buttons:
                button.is_hover = False

        if(not self.is_notification_on()):
            self.current_state.on_update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):

        for box in self.popups.copy().values():
            box.on_key_press(symbol, modifiers)

        if(not self.is_notification_on()):
            self.current_state.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        if(not self.is_notification_on()):
            self.current_state.on_key_release(symbol, modifiers)



def main():
    window = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
