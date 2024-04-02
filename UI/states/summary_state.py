import arcade
from .state import State
from ..buttons import ImageButton, HoverLineButton
from config.config import *


class SummaryState(State):
    def __init__(self, game, mode, score):
        super().__init__(game)

        self.result_title = arcade.load_texture("resources/images/resultTitle.png")
        self.your_score_title = arcade.load_texture("resources/images/yourScoreTitle.png")
        self.top_title = arcade.load_texture("resources/images/topTitle.png")

        self.mode_label = arcade.load_texture("resources/images/traditionalModeLabel.png")
        self.font = arcade.load_font("resources/fonts/PaytoneOne-Regular.ttf")

        self.font2 = arcade.load_font("resources/fonts/UTM ANDROGYNE.TTF")

        self.score = self.game.proxy.get_user_score(score)


        self.back_button = HoverLineButton("resources/images/btnBack.png")
        self.back_button.center_x = SCREEN_WIDTH // 2
        self.back_button.center_y = SCREEN_HEIGHT // 2 - 230

        self.back_button.on_click = lambda : self.game.return_menu()

        self.buttons.extend([self.back_button])




    def get_top(self):
        return self.game.proxy.get_user_top()


    def draw(self):
        super().draw()
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 + 150, 
                                             self.result_title, 0.75)
        
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT//2 + 120, 
                                             self.mode_label, 0.5)
        
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 + 90, 
                                             self.your_score_title, 0.6)
        
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 - 40,
                                                self.top_title, 0.6)
        
        arcade.draw_text(str(self.score), SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT//2 + 10, arcade.color.ORANGE_RED, 40, font_name=self.font2, align="center", width=100)

        arcade.draw_text(str(self.get_top()), SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT//2 - 120, arcade.color.VIVID_VIOLET, 40, font_name=self.font2, align="center", width=100)
        
        


                    

    