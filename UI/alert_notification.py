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
        for button in self.buttons:
            button.on_update(delta_time)

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        for button in self.buttons:
            button.on_mouse_press(x, y, button, modifiers)

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
            button.draw_additional_elements()

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

        self.font = arcade.load_font("resources/fonts/UTM ANDROGYNE.TTF")


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
            x = SCREEN_WIDTH // 2 - 120,
            y = SCREEN_HEIGHT // 2 - 40,
            width = 200,
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
            
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 5, self.submission_box)
