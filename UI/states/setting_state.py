from .state import State

class SettingsState(State):
    def __init__(self, game):
        super().__init__(game)

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass
