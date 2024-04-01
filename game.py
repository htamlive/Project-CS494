import arcade
from UI.states.menu_state import MenuState
from config.config import *


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.WHITE)

        # Load the background image
        self.background = arcade.load_texture("resources/images/background.png")
        self.title = arcade.load_texture("resources/images/title.png")
        self.paper = arcade.load_texture("resources/images/paper.png")

        # Stack of states
        self.state_stack = []

        # Set initial state
        self.menu_state = MenuState(self)

        self.push_state(self.menu_state)

    def push_state(self, new_state):
        self.state_stack.append(new_state)

    def pop_state(self):
        if len(self.state_stack) > 1:
            self.state_stack.pop()
        
        self.current_state.on_update(0)
    
    def return_menu(self):
        while len(self.state_stack) > 1:
            self.state_stack.pop()


    @property
    def current_state(self):
        return self.state_stack[-1]

    def on_draw(self):
        arcade.start_render()

        # Draw the background image
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        # Draw the title
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, 500, 90, self.title)

        # Draw the paper
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, 400, 500, self.paper)

        if(self.current_state):
            self.current_state.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.current_state.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        self.current_state.on_mouse_press(x, y, button, modifiers)

    def on_update(self, delta_time: float):
        self.current_state.on_update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        self.current_state.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.current_state.on_key_release(symbol, modifiers)



def main():
    window = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
