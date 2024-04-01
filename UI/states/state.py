class State:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        
    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        for button in self.buttons:
            button.on_mouse_press(x, y, button, modifiers)

    def on_update(self, delta_time):
        for button in self.buttons:
            button.on_update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_key_release(self, symbol: int, modifiers: int):
        pass

    def on_draw(self):
        for button in self.buttons:
            button.on_draw()


    def draw(self):
        for button in self.buttons:
            button.draw()
