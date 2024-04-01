import arcade
from .state import State


class SummaryState(State):
    def __init__(self, game, mode, scores):
        super().__init__(game)

    def on_entry(self):
        self.context.ui.show_summary()
        self.context.ui.show_summary_buttons()

    def on_exit(self):
        self.context.ui.hide_summary()
        self.context.ui.hide_summary_buttons()

    def on_summary_button_click(self, button):
        if button == 'back':
            self.context.transition_to('main_menu')
        elif button == 'exit':
            self.context.transition_to('exit')