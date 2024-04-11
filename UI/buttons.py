import arcade

class ImageButton(arcade.Sprite):
    def __init__(self, image, scale=1):
        super().__init__(image, scale)

        self.origin_scale = scale

        self.is_hover = False
        self.on_click = lambda: None

        self.is_clicked = False
        self.click_animation_duration = 0.1
        self.click_timer = 0
        self.click_scale_factor = 1.2

        self.prev_mouse_position = [-1, -1]

        self.is_enabled = True

        self.verbose = False

    def on_mouse_motion(self, x, y, dx, dy):
        self.prev_mouse_position = [x, y]

        if self.left <= x <= self.right and self.bottom <= y <= self.top and self.is_enabled:
            self.is_hover = True
        else:
            self.is_hover = False

        # if(self.verbose):
        #     print(self.is_hover, self.is_enabled)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.is_hover and self.is_enabled:
            # print("clicked")
            self.is_clicked = True
            self.click_timer = self.click_animation_duration

    def on_update(self, delta_time: float = 1 / 60):
        if self.is_clicked and self.is_enabled:
            self.click_timer -= delta_time
            if self.click_timer <= 0:
                self.is_clicked = False
                self.click_timer = 0
                self.on_click()

    def check_hover(self):
        if self.left <= self.prev_mouse_position[0] <= self.right and self.bottom <= self.prev_mouse_position[1] <= self.top:
            self.is_hover = True
        else:
            self.is_hover = False
            self.is_clicked = False

    def set_enabled(self, enabled, visible=True):
        self.is_enabled = enabled
        self.visible = visible

        if(not self.is_enabled):
            self.is_hover = False
            self.is_clicked = False
        else:
            self.check_hover()

    def draw_effect(self):
        pass
        


    def draw(self, *, filter=None, pixelated=None, blend_function=None):
        
        pass
            
            
            


class HoverLineButton(ImageButton):
    def __init__(self, image, scale=1, line_color=arcade.color.BLACK):
        super().__init__(image, scale)

        self.line_height = 2
        self.line_color = line_color

        self.hovered_line_width = 10
        self.hovered_line_max_width = self.width
        self.hovered_line_speed = 20
        self.hovered_line_current_width = 0
        self.hovered_line_timer = 0

    def draw_effect(self):
        if self.hovered_line_timer > 0 and self.is_enabled:
            arcade.draw_line(
                self.center_x - self.hovered_line_current_width // 2,
                self.center_y - self.height // 2 - self.line_height // 2,
                self.center_x + self.hovered_line_current_width // 2,
                self.center_y - self.height // 2 - self.line_height // 2,
                self.line_color,
                self.line_height
            )

    def draw(self, draw_with_effect = True, verbose = False):
        super().draw(draw_with_effect = False, verbose = verbose)
        


    def on_update(self, delta_time):
        super().on_update(delta_time)
        if(self.is_enabled):
            if self.is_hover:
                if self.hovered_line_current_width + self.hovered_line_speed < self.hovered_line_max_width:
                    self.hovered_line_timer += delta_time
                    if self.hovered_line_timer > 0.05:
                        self.hovered_line_current_width += self.hovered_line_speed
                else:
                    self.hovered_line_current_width = self.hovered_line_max_width
            else:
                if self.hovered_line_current_width - self.hovered_line_speed > 0:
                    self.hovered_line_timer -= delta_time
                    if self.hovered_line_timer >= 0:
                        self.hovered_line_current_width -= self.hovered_line_speed
                else:
                    self.hovered_line_timer = 0
                    self.hovered_line_current_width = 0
