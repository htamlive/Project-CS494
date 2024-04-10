import arcade
from .state import State
from ..buttons import ImageButton, HoverLineButton
from config.config import *


class SummaryState(State):
    def __init__(self, game, mode, score, type_of_summary, winner_name = None):
        super().__init__(game)

        self.result_title = arcade.load_texture("resources/images/resultTitle.png")
        self.your_score_title = arcade.load_texture("resources/images/yourScoreTitle.png")
        self.champion_title = arcade.load_texture("resources/images/championTitle.png")
        self.top_title = arcade.load_texture("resources/images/topTitle.png")

        self.type_of_summary = type_of_summary
        self.winner_name = winner_name

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
        

        
        if(self.type_of_summary == Summary_type.WINNER):

            user_name = self.game.proxy.get_user_name()
            if(user_name == self.winner_name):
                arcade.draw_text("You are", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT//2 + 100, arcade.color.BLACK, 12, font_name=self.font2, align="center", width=200)

            arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 + 110 - 30,
                                                self.champion_title, 0.5)

            arcade.draw_text(self.winner_name, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT//2 + 60 - 40, arcade.color.RED, 20, font_name=self.font, align="center", width=200)

            arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT//2 - 40 -10, 
                                             self.your_score_title, 0.6)
        
            arcade.draw_text(str(self.score), SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT//2 - 120, arcade.color.ORANGE_RED, 40, font_name=self.font2, align="center", width=100)
           

            arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT//2 - 43 - 10,
                                                self.top_title, 0.6)
        

            arcade.draw_text(str(self.get_top()), SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT//2 - 120, arcade.color.VIVID_VIOLET, 40, font_name=self.font2, align="center", width=100)
        
        elif(self.type_of_summary == Summary_type.DISQUALIFIED):
            arcade.draw_text("DISQUALIFIED", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT//2 + 10, arcade.color.RED, 40, font_name=self.font2, align="center", width=200)
        


                    

    