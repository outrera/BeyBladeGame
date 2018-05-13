import os
from random import shuffle, choice
from types import *

import numpy as np

from globals import *
from graphic_effects import *
from screen import Screen
from text import Text
from buttons import TextButton

BB_WIDTH, BB_HEIGHT = 120, 120
FRAMES_TIMER = 1200
MAX_SPEED = 5


def shuffle_bb_list(player_bb_name):
    assert type(player_bb_name) is StringType, "player is not a name string!"
    rnd_bb_list = [i for i in BEYBLADES_LIST]  # copy the list
    rnd_bb_list.remove(player_bb_name)
    shuffle(rnd_bb_list)  # shuffle works in place and returns None
    return rnd_bb_list


def get_player_bb_dict(player_bb_name):
    image = player_bb_name + '.png'
    image_surf = pygame.image.load(os.path.join(graphics_path, image)).convert_alpha()
    image_surf = pygame.transform.smoothscale(image_surf, (BB_WIDTH, BB_HEIGHT))
    centerx = int(WIDTH / 2.0) - int(BB_WIDTH / 2.0)
    image_surf_rect = image_surf.get_rect(center=(centerx, int(HEIGHT / 2.0)))
    player_dict = {"name": player_bb_name,
                   "image": image_surf,
                   "rect": image_surf_rect}
    return player_dict


class CampaignScreen(Screen):
    def __init__(self, display_surf, logger, player_bb_name):
        super(CampaignScreen, self).__init__(display_surf=display_surf, logger=logger)
        self._player_bb_dict = get_player_bb_dict(player_bb_name)
        self._rival_bb_dict = self.get_bb_dict()
        self._next_opponent_bb = self.get_next_opponent()
        self._frames_counter = 0
        self._r = np.logspace(0, 0.5, FRAMES_TIMER)  # create a non-linear list 0->~3.16

        self._player_bb_txt_obj = None
        self._player_bb_txt_fade_box = None
        self._opponent_bb_txt_obj = None
        self._oppnenet_bb_txt_fade_box = None

        self._continue_button = None

    def on_update(self):

        move_spdy = 1

        if self._frames_counter < FRAMES_TIMER - 1:
            self._frames_counter += 1
            move_spdy = MAX_SPEED - self._r[self._frames_counter]  # keep slowing down

        elif self._next_opponent_bb["rect"].top == self._player_bb_dict["rect"].top:
            move_spdy = 0
            if self._player_bb_txt_obj is None:
                self.create_fade_in_text()
        # else:
        #     move_spdy = MAX_SPEED - self._r[self._frames_counter]  # keep slowing down

        for bb in self._rival_bb_dict.values():
            bb["rect"].top = (bb["rect"].top + move_spdy) % HEIGHT

        if self._player_bb_txt_obj is not None:
            self._player_bb_txt_obj.on_update()
            self._opponent_bb_txt_obj.on_update()
            self._player_bb_txt_fade_box.on_update()
            if self._oppnenet_bb_txt_fade_box.on_update():
                # finished fade in transition
                if self._continue_button is None:
                    self._continue_button = TextButton(self.logger, 100, 50, int(WIDTH * 4.0/5), int(HEIGHT * 7.0 / 8),
                                                       "Continue", WHITE, RED, BRIGHTYELLOW, 32)
                elif self._continue_button.on_update(self._mouse_clicked, self._mousex, self._mousey):
                    self.on_exit(None)

        return

    def on_render(self):

        g_left = None
        self._display_surf.fill(BLACK)

        # draw player
        image = self._player_bb_dict["image"]
        left = self._player_bb_dict["rect"].left
        top = self._player_bb_dict["rect"].top
        self._display_surf.blit(image, (left, top))

        # draw opponents moving column
        for bb in self._rival_bb_dict.values():
            image = bb["image"]
            left = bb["rect"].left
            if g_left is None:
                g_left = left
            top = bb["rect"].top

            self._display_surf.blit(image, (left, top))

        # draw top gradient
        draw_vertical_gradient_box(self._display_surf, BB_WIDTH, BB_HEIGHT * 3, g_left, 0, BLACK, GRADIENT_DOWN, 20)
        # draw bottom gradient
        draw_vertical_gradient_box(self._display_surf, BB_WIDTH, BB_HEIGHT * 3, g_left, HEIGHT - BB_HEIGHT * 3, BLACK,
                                   GRADIENT_UP, 20)

        if self._player_bb_txt_obj is not None:
            self._player_bb_txt_obj.on_render(self._display_surf)
            self._opponent_bb_txt_obj.on_render(self._display_surf)
            self._player_bb_txt_fade_box.on_render(self._display_surf)
            self._oppnenet_bb_txt_fade_box.on_render(self._display_surf)

        if self._continue_button is not None:
            self._continue_button.on_render(self._display_surf)

        super(CampaignScreen, self).on_render()
        return

    def on_exit(self, key):
        self._running = False
        from battle_screen import BattleScreen
        self._next_screen = BattleScreen
        return

    def get_next_opponent(self):
        possible_rivals_list = []
        for bb in self._rival_bb_dict.values():
            if bb["played"] is False:
                possible_rivals_list.append(bb)
        opponent = choice(possible_rivals_list)
        self.logger.info("Random opponent selected: {}".format(opponent["name"]))
        return opponent

    def get_bb_dict(self):
        rival_bb_list = shuffle_bb_list(self._player_bb_dict["name"])
        bb_dict = {}
        centerx = int(WIDTH / 2.0) + int(BB_WIDTH / 2.0)
        for bb in rival_bb_list:
            centery = HEIGHT - int(BB_HEIGHT / 2.0) - BB_HEIGHT * rival_bb_list.index(bb)
            image = bb + ".png"
            image_surf = pygame.image.load(os.path.join(graphics_path, image)).convert_alpha()
            image_surf = pygame.transform.smoothscale(image_surf, (BB_WIDTH, BB_HEIGHT))
            image_surf_rect = image_surf.get_rect(center=(centerx, centery))
            bb_dict[bb] = {"name": bb,
                           "image": image_surf,
                           "rect": image_surf_rect,
                           "played": False}
        return bb_dict

    def create_fade_in_text(self):
        name = self._player_bb_dict["name"]
        rect = self._player_bb_dict["rect"]
        self._player_bb_txt_obj = Text(name, int(WIDTH / 4.0), rect.centery, WHITE, BLACK, WHITE)
        txt_rect = self._player_bb_txt_obj.get_rect()
        self._player_bb_txt_fade_box = FadeInBox(txt_rect.width, txt_rect.height,
                                                 txt_rect.top, txt_rect.left,
                                                 BLACK, 255)
        name = self._next_opponent_bb["name"]
        rect = self._next_opponent_bb["rect"]
        self._opponent_bb_txt_obj = Text(name, int(WIDTH * 3.0 / 4), rect.centery, WHITE, BLACK, WHITE)
        txt_rect = self._opponent_bb_txt_obj.get_rect()
        self._oppnenet_bb_txt_fade_box = FadeInBox(txt_rect.width, txt_rect.height,
                                                   txt_rect.top, txt_rect.left,
                                                   BLACK, 255)
        return