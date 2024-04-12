import arcade
from .buttons import HoverLineButton
from arcade.gui import UIManager, UIInputText
from config.config import *

class NotificationBase:
    def __init__(self):
        self.enabled = False
        self.buttons = arcade.sprite_list.SpriteList()

    def set_enabled(self, enabled):
        self.enabled = enabled
        for button in self.buttons:
            button.set_enabled(enabled)

    def on_update(self, delta_time):
        if(not self.enabled):
            return
        for button in self.buttons:
            button.on_update(delta_time)

    def on_mouse_motion(self, x, y, dx, dy):
        if(not self.enabled):
            return
        for button in self.buttons:
            button.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        if(not self.enabled):
            return
        for button in self.buttons:
            button.on_mouse_press(x, y, button, modifiers)

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def draw(self):
        pass




class AlertNotification(NotificationBase):
    def __init__(self, message, on_ok=lambda: None, on_cancel=lambda: None):
        super().__init__()
        self.message = message
        self.on_ok = on_ok
        self.on_cancel = on_cancel

        self.alert_box = arcade.load_texture("resources/images/rectangleBorder.png")
        self.ok_button = HoverLineButton("resources/images/btnOK.png")
        self.ok_button.center_x = SCREEN_WIDTH // 2 - 80
        self.ok_button.center_y = SCREEN_HEIGHT // 2 - 50
        self.ok_button.hovered_line_speed = 10

        self.cancel_button = HoverLineButton("resources/images/btnCancel.png")
        self.cancel_button.center_x = SCREEN_WIDTH // 2 + 80
        self.cancel_button.center_y = SCREEN_HEIGHT // 2 - 50
        self.cancel_button.hovered_line_speed = 10

        self.ok_button.on_click = self.on_ok
        self.cancel_button.on_click = self.on_cancel



        self.buttons.append(self.ok_button)
        self.buttons.append(self.cancel_button)

    def draw(self):
        if not self.enabled:
            return
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.alert_box, 1.5)

        self.buttons.draw()

        for button in self.buttons:
            button.draw_effect()

        arcade.draw_text(self.message, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, arcade.color.BLACK, 20,
                         align="center", width=300)

class OKNotification(NotificationBase):
    def __init__(self, message, on_ok=lambda: None):
        super().__init__()
        self.message = message
        self.on_ok = on_ok

        self.alert_box = arcade.load_texture("resources/images/rectangleBorder.png")
        self.ok_button = HoverLineButton("resources/images/btnOK.png")
        self.ok_button.center_x = SCREEN_WIDTH // 2
        self.ok_button.center_y = SCREEN_HEIGHT // 2 - 50

        self.ok_button.on_click = self.on_ok

        self.ok_button.hovered_line_speed = 10
        self.buttons.extend([self.ok_button])

    def draw(self):
        if not self.enabled:
            return
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.alert_box, 1.5)

        self.buttons.draw()

        for button in self.buttons:
            button.draw_effect()

        arcade.draw_text(self.message, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, arcade.color.BLACK, 20,
                         align="center", width=300)
        

class InputPopup(NotificationBase):
    def __init__(self, message, on_ok=lambda: None, on_cancel=lambda: None):
        super().__init__()
        self.message = message
        self.on_ok = on_ok
        self.on_cancel = on_cancel

        self.message_noti = ""
        self.message_noti_color = arcade.color.GREEN

        self.submission_box = arcade.load_texture("resources/images/submissionBox.png")

        self.alert_box = arcade.load_texture("resources/images/rectangleBorder.png")
        self.ok_button = HoverLineButton("resources/images/btnOK.png")
        self.ok_button.center_x = SCREEN_WIDTH // 2 - 80
        self.ok_button.center_y = SCREEN_HEIGHT // 2 - 80
        self.ok_button.hovered_line_speed = 10

        self.cancel_button = HoverLineButton("resources/images/btnCancel.png")
        self.cancel_button.center_x = SCREEN_WIDTH // 2 + 80
        self.cancel_button.center_y = SCREEN_HEIGHT // 2 - 80
        self.cancel_button.hovered_line_speed = 10

        arcade.load_font("resources/fonts/UTM ANDROGYNE.TTF")

        self.font = "UTM Androgyne"


        self.ok_button.on_click = self.on_ok
        self.cancel_button.on_click = self.on_cancel

        self.buttons.append(self.ok_button)
        self.buttons.append(self.cancel_button)

        self.ui_manager = UIManager()
        self.ui_manager.enable()
        self.input_box = self.init_input_box()

        self.ui_manager.add(self.input_box)


    def init_input_box(self):
        return UIInputText(
            x = SCREEN_WIDTH // 2 - 150,
            y = SCREEN_HEIGHT // 2 - 40,
            width = 290,
            height = 50,
            font_name = self.font,
            font_size = 20,
            text=''
        )
    
    def show_noti(self, message, color):
        self.message_noti = message
        self.message_noti_color = color
    
    def get_current_text(self):
        return self.input_box.text

    def set_enabled(self, enabled):
        super().set_enabled(enabled)
        self.input_box._active = False

    def on_update(self, delta_time):
        super().on_update(delta_time)
        self.ui_manager.on_update(delta_time)

    def on_mouse_motion(self, x, y, dx, dy):
        super().on_mouse_motion(x, y, dx, dy)
        self.ui_manager.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(x, y, button, modifiers)
        self.ui_manager.on_mouse_press(x, y, button, modifiers)

    def draw(self):
        if not self.enabled:
            return
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.alert_box, 1.5)

        self.buttons.draw()

        for button in self.buttons:
            button.draw_effect()


        self.ui_manager.draw()
        arcade.draw_text(self.message, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, arcade.color.BLACK, 20,
                         align="center", width=300)
        
        if(self.message_noti):
            arcade.draw_text(self.message_noti, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20, self.message_noti_color, 11,
                         align="center", width=300)
            
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10, self.submission_box, 1.2)

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


class WaitingNotification(NotificationBase):
    def __init__(self, message):
        super().__init__()
        self.message = message

        self.alert_box = arcade.load_texture("resources/images/rectangleBorder.png")

        self.query_func = []

        self.accumulated_dot = 0
        self.speed = 1.5

        arcade.load_font("resources/fonts/UTM ANDROGYNE.TTF")
        arcade.load_font("resources/fonts/PaytoneOne-Regular.ttf")
        self.font = "Paytone One"

    def add_query(self, query_func):
        self.query_func.append(query_func)

    def on_update(self, delta_time):
        super().on_update(delta_time)
        self.set_enabled(len(self.query_func) != 0)

        self.accumulated_dot += delta_time * self.speed

        if(self.accumulated_dot >= 4):
            self.accumulated_dot = 0

        for idx, query in enumerate(self.query_func.copy()):
            if query():
                self.query_func[idx] = None

        self.query_func = [query for query in self.query_func if query is not None]


    def draw(self):
        if not self.enabled:
            return
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.alert_box, 1.5)

        self.buttons.draw()

        for button in self.buttons:
            button.draw_effect()

        add_dot = '.' * (int(self.accumulated_dot))

        arcade.draw_text(self.message + add_dot, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20, arcade.color.BLACK, 20,
                         align="center", width=300,font_name=self.font)
        


class QuestResultNotification(NotificationBase):
    def __init__(self, result, on_ok=lambda: None):
        super().__init__()
        self.on_ok = on_ok

        self.result = result

        self.alert_box = arcade.load_texture("resources/images/rectangleBorder.png")

        self.results = {
            Result.CORRECT: arcade.load_texture("resources/images/correctResult.png"),
            Result.INCORRECT: arcade.load_texture("resources/images/incorrectResult.png"),
        }


    def draw(self):
        if not self.enabled:
            return
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.alert_box, 1.5)


        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, self.results[self.result], 1.5)

        # arcade.draw_text(self.message, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, arcade.color.BLACK, 20,
        #                  align="center", width=300)