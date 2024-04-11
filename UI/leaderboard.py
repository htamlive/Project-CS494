import arcade
from config.config import *
from .buttons import HoverLineButton, ImageButton

class Leaderboard:
    def __init__(self, proxy):
        self.players_info = []
        self.current_page = 0
        self.player_per_page = 3
        self.racing_length = None
        self.proxy = proxy

        self.leaderboard_title = arcade.load_texture("resources/images/leaderboardTitle.png")
        arcade.load_font("resources/fonts/PaytoneOne-Regular.ttf")

        self.font = "Paytone One"

        left_arrow_button = HoverLineButton("resources/images/leftArrow.png", 0.15)
        left_arrow_button.click_scale_factor = 0.3
        left_arrow_button.center_x = SCREEN_WIDTH - 200
        left_arrow_button.center_y = SCREEN_HEIGHT//2 + 10 + 40
        left_arrow_button.hovered_line_speed = 5

        right_arrow_button = HoverLineButton("resources/images/rightArrow.png", 0.15)
        right_arrow_button.click_scale_factor = 0.3
        right_arrow_button.center_x = SCREEN_WIDTH - 60 - 10
        right_arrow_button.center_y = SCREEN_HEIGHT//2 + 10 + 40
        right_arrow_button.hovered_line_speed = 5

        self.buttons = arcade.SpriteList()
        self.buttons.extend([left_arrow_button, right_arrow_button])

        def on_left_arrow():
            if self.current_page > 0:
                self.current_page -= 1

        def on_right_arrow():
            
            if (self.current_page + 1)*self.player_per_page< len(self.players_info):
                self.current_page += 1

        left_arrow_button.on_click = on_left_arrow
        right_arrow_button.on_click = on_right_arrow

    def get_current_players_with_scores(self):

        return self.proxy.get_current_players_with_scores()

    def check_diff_players(self, players):
        if len(self.players_info) != len(players):
            return True
        for i in range(len(players)):
            if self.players_info[i][0] != players[i][0] or self.players_info[i][1] != players[i][1]:
                return True
        return False

    def update(self, delta_time):
        players = self.get_current_players_with_scores()
        if players != Socket_return.IS_WAITING:
            players = sorted(players, key=lambda x: x[1], reverse=True)
            if(self.check_diff_players(players)):
                self.current_page = 0
                self.players_info = players

        if(len(self.players_info) == 0):
            self.buttons[0].set_enabled(False, False)
            self.buttons[1].set_enabled(False, False)
        else:
            enable_left = self.current_page > 0
            enable_right = (self.current_page + 1) * self.player_per_page < len(self.players_info)
            self.buttons[0].set_enabled(enable_left, enable_left)
            self.buttons[1].set_enabled(enable_right, enable_right)

            


    def draw(self):
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH - 140, SCREEN_HEIGHT//2 + 80,
                                                self.leaderboard_title)
        
        jump_step = 30
        if(self.current_page * self.player_per_page < len(self.players_info) and self.racing_length is not None):
            for idx, (player_name, score) in enumerate(self.players_info[self.current_page * self.player_per_page: (self.current_page + 1) * self.player_per_page]):
                arcade.draw_text(player_name, SCREEN_WIDTH - 240, SCREEN_HEIGHT - 320 - idx * jump_step, arcade.color.BLACK, 14, font_name=self.font, align="right", width=100)
                arcade.draw_text(f'{str(score)}/{self.racing_length}', SCREEN_WIDTH - 100, SCREEN_HEIGHT - 320 - idx * jump_step, arcade.color.BLACK, 14, font_name=self.font)

