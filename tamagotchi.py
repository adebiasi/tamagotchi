# Code created starting from https://gist.github.com/ryesalvador/e88cb2b4bbe0694d175ef2d7338abd07

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from enum import Enum

import pygame, random, sys, os, platform
from pygame.locals import *


class CreatureSM(object):
    class States(Enum):
        IDLE = 0
        EAT = 1
        CLEAN = 2
        SLEEP = 3
        DEATH = 4

    class Transitions(Enum):
        NONE = 0
        IDLE_TO_IDLE = 1
        IDLE_TO_EAT = 2
        EAT_TO_EAT = 3
        EAT_TO_IDLE = 4
        IDLE_TO_CLEAN = 5
        CLEAN_TO_CLEAN = 6
        CLEAN_TO_IDLE = 7
        IDLE_TO_SLEEP = 8
        SLEEP_TO_SLEEP = 9
        SLEEP_TO_IDLE = 10
        IDLE_TO_DEATH = 11

    def __init__(self):
        self.__current_state__ = None
        self.__current_transition__ = None
        self.set_current_state(self.States.IDLE, self.Transitions.NONE)
        self.current_state_counter = 0

    def set_current_state(self, state, transition):
        self.__current_state__ = state
        self.current_state_counter = 0
        self.set_current_transition(transition)

    def set_current_transition(self, transition):
        self.__current_transition__ = transition

    def current_state_is(self, state):
        return self.__current_state__ is state


class Creature(CreatureSM):
    AGE_HATCH = 128
    AGE_MATURE = 796
    AGE_DEATH_FROM_NATURAL_CAUSES = 8192
    HUNGER_CAN_EAT = 32
    HUNGER_NEEDS_TO_EAT_LEVEL = 128
    HUNGER_SICK_FROM_NOT_EATING = 256
    HUNGER_DEAD_FROM_NOT_EATING_LEVEL = 512
    ENERGY_CAN_SLEEP = 150
    ENERGY_TIRED_LEVEL = 64
    ENERGY_PASS_OUT = 8
    WASTE_EXPUNGE_LEVEL = 256

    def __init__(self):
        super(Creature, self).__init__()
        self.status = {'hunger': 0, 'energy': 256, 'waste': 0, 'age': 0, 'happiness': 0}
        self.signals = {'stink': 0, 'exclaim': 0}
        self.stage = 0

    def handle_evolution(self):
        if self.stage == 0 and self.status['age'] > self.AGE_HATCH:
            self.stage += 1
        if self.stage == 1 and self.status['age'] > self.AGE_MATURE:
            self.stage += 1

    def do_random_event(self):
        num = random.randint(0, 31)
        if num == 12:
            self.status['hunger'] += 1
        elif num == 16:
            self.status['energy'] -= 1
        elif num == 18:
            self.status['energy'] += 1
        elif num == 20:
            self.status['waste'] += 1
        elif num == 7:
            self.status['happiness'] += 1
        elif num == 4:
            self.status['happiness'] -= 1

    def do_step(self):
        self.do_random_event()
        self.status['hunger'] += 1
        self.status['waste'] += 1
        self.status['energy'] -= 1
        self.status['age'] += 2
        if self.status['waste'] >= self.WASTE_EXPUNGE_LEVEL:
            self.status['happiness'] -= 1

    def get_debug_info(self):
        debug_info = self.status.copy()
        debug_info['state']= self.__current_state__.name
        debug_info['transition'] = self.__current_transition__.name
        return debug_info

class TamagotchiEmulator:
    if platform.system() == 'Windows':
        os.environ['SDL_VIDEODRIVER'] = 'windib'

    UPDATE_GAME_LOGIC_EVENT = USEREVENT + 1
    SECOND = 1000

    class COMMANDS(Enum):
        NONE = -1
        EAT = 0
        CLEAN = 1
        SWITCH_LIGHT = 3

    def __init__(self):
        self.light = True
        self.creature = Creature()

    def main(self):
        pygame.init()
        pygame.time.set_timer(self.UPDATE_GAME_LOGIC_EVENT, self.SECOND)
        g_interface = GraphicalInterface();
        curr_command = self.COMMANDS.NONE
        update_game_logic = False

        # Game loop
        while True:
            g_interface.clean_screen()

            # Event handler
            for _ in pygame.event.get(self.UPDATE_GAME_LOGIC_EVENT):
                update_game_logic = True

            g_interface.main_display.update_animation_event()

            g_interface.handle_gui_event()

            if g_interface.curr_cmd is not None:
                curr_command = g_interface.curr_cmd['command']

            # Game logic
            if update_game_logic:
                # evolution phase
                self.creature.handle_evolution()

                # state phase
                if curr_command == self.COMMANDS.SWITCH_LIGHT:
                    self.light = not self.light

                if self.creature.current_state_is(self.creature.States.IDLE):
                    self.creature.do_step()

                    if self.creature.stage > 0:
                        if self.creature.status['hunger'] >= self.creature.HUNGER_DEAD_FROM_NOT_EATING_LEVEL or \
                                self.creature.status[
                                    'age'] >= self.creature.AGE_DEATH_FROM_NATURAL_CAUSES:
                            self.creature.set_current_state(self.creature.States.DEATH,
                                                            self.creature.Transitions.IDLE_TO_DEATH)
                        elif self.light and curr_command == self.COMMANDS.EAT:
                            self.creature.set_current_state(self.creature.States.EAT,
                                                            self.creature.Transitions.IDLE_TO_EAT)
                        elif self.light and curr_command == self.COMMANDS.CLEAN:
                            self.creature.set_current_state(self.creature.States.CLEAN,
                                                            self.creature.Transitions.IDLE_TO_CLEAN)
                        elif not self.light and self.creature.status['energy'] <= self.creature.ENERGY_CAN_SLEEP:
                            self.creature.set_current_state(self.creature.States.SLEEP,
                                                            self.creature.Transitions.IDLE_TO_SLEEP)
                        elif self.creature.status['energy'] < self.creature.ENERGY_PASS_OUT:
                            self.creature.status['happiness'] -= 64
                            self.creature.set_current_state(self.creature.States.SLEEP,
                                                            self.creature.Transitions.IDLE_TO_SLEEP)
                elif self.creature.current_state_is(self.creature.States.EAT):
                    if self.creature.current_state_counter == 6:
                        self.creature.set_current_state(self.creature.States.IDLE,
                                                        self.creature.Transitions.EAT_TO_IDLE)
                        self.creature.status['hunger'] = 0
                    else:
                        self.creature.set_current_transition(self.creature.Transitions.EAT_TO_EAT)
                elif self.creature.current_state_is(self.creature.States.SLEEP):
                    if self.creature.status['energy'] >= 256 or self.light:
                        self.creature.set_current_state(self.creature.States.IDLE,
                                                        self.creature.Transitions.SLEEP_TO_IDLE)
                    else:
                        self.creature.set_current_transition(self.creature.Transitions.SLEEP_TO_SLEEP)
                        self.creature.status['energy'] += 8
                elif self.creature.current_state_is(self.creature.States.CLEAN):
                    if self.creature.current_state_counter == 4:
                        self.creature.set_current_state(self.creature.States.IDLE,
                                                        self.creature.Transitions.CLEAN_TO_IDLE)
                        self.creature.status['waste'] = 0
                    else:
                        self.creature.set_current_transition(self.creature.Transitions.CLEAN_TO_CLEAN)
                curr_command = self.COMMANDS.NONE

                # signal phase
                if self.creature.status['waste'] >= self.creature.WASTE_EXPUNGE_LEVEL:
                    self.creature.signals['stink'] += 1
                else:
                    self.creature.signals['stink'] = 0
                if self.creature.status['energy'] <= self.creature.ENERGY_TIRED_LEVEL or self.creature.status[
                    'hunger'] >= self.creature.HUNGER_NEEDS_TO_EAT_LEVEL \
                        or self.creature.status[
                    'waste'] >= self.creature.WASTE_EXPUNGE_LEVEL - self.creature.WASTE_EXPUNGE_LEVEL / 3:
                    self.creature.signals['exclaim'] += 1
                else:
                    self.creature.signals['exclaim'] = 0

                update_game_logic = False
                self.creature.current_state_counter += 1

            g_interface.update_animation(self.creature.__current_state__, self.creature.__current_transition__,
                                         self.creature.stage, self.creature.signals['stink'],
                                         self.creature.signals['exclaim'])

            g_interface.render_buttons()
            g_interface.render_debug_info(self.creature.get_debug_info())
            g_interface.render_main_display(not self.light)


class GraphicalInterface:
    FPS = 30
    SCREEN_WIDTH = 550
    SCREEN_HEIGHT = 400

    # Colors
    BG_COLOR = (160, 178, 129)
    PIXEL_COLOR = (10, 12, 6)
    NON_PIXEL_COLOR = (156, 170, 125)

    class MainDisplay:

        UPDATE_ANIMATION_EVENT = USEREVENT + 2
        SECOND = 1000
        # Animations
        __IDLE_EGG__ = (
            (0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7e000,
             0x87000, 0x103800, 0x300c00, 0x700400, 0x418200, 0x418200, 0x400200, 0x700600, 0x3c0c00, 0x1e0800,
             0x3ffc00, 0x0), (
                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                0x7e000,
                0x87000, 0x103800, 0x300c00, 0x700400, 0x400200, 0x418200, 0x418200, 0x700600, 0x3c0c00, 0xffff00,
                0x0))
        __IDLE_BABY__ = (
            (0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
             0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x78000, 0xb4000, 0x1fe000), (
                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                0x0,
                0x0, 0x0, 0x0, 0x0, 0x78000, 0xcc000, 0x84000, 0xb4000, 0x84000, 0x78000, 0x0))
        __IDLE_MATURE__ = (
            (0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xfc00, 0x10200, 0x24900, 0x20100, 0x23100, 0x20100,
             0x20100, 0x10200, 0xfc00, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0), (
                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xfc00, 0x10200, 0x28500, 0x23100,
                0x23100,
                0x20100, 0x10200, 0xfc00, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0))
        __SLEEP_BABY__ = (
            (0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
             0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x78000, 0xfc000, 0x1fe000), (
                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                0x0,
                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1fe000, 0x3ff000))
        __SLEEP_MATURE__ = ((
                                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                                0x0,
                                0x0,
                                0x0,
                                0x0,
                                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3fc00, 0x40200, 0x80100), (
                                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                                0x0,
                                0x0,
                                0x0,
                                0x0,
                                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1f800, 0x20400, 0x40200, 0x40200))

        IDLE_ANIMATIONS = [__IDLE_EGG__, __IDLE_BABY__, __IDLE_MATURE__]
        SLEEP_ANIMATIONS = [None, __SLEEP_BABY__, __SLEEP_MATURE__]

        OVERLAY_ZZZ = ((0x0, 0x0, 0x0, 0x0, 0xf800000, 0x4000000, 0x2000000, 0x1000000, 0xf800000, 0x0, 0x0, 0x3c00000,
                        0x1000000, 0x800000, 0x3c00000, 0x0, 0x700000, 0x200000, 0x700000, 0x0, 0x80000, 0x0, 0x0, 0x0,
                        0x0,
                        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0), (
                           0x0, 0x0, 0x0, 0xf800000, 0x4000000, 0x2000000, 0x1000000, 0xf800000, 0x0, 0x0, 0x3c00000,
                           0x1000000,
                           0x800000, 0x3c00000, 0x0, 0x700000, 0x200000, 0x700000, 0x0, 0x80000, 0x0, 0x0, 0x0, 0x0,
                           0x0,
                           0x0,
                           0x0,
                           0x0, 0x0, 0x0, 0x0, 0x0))
        OVERLAY_EAT = (
            (0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x4000000, 0x2000000, 0x7700000, 0xff00000, 0xfd00000, 0xff00000,
             0x7f00000, 0x7e00000, 0x3c00000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
             0x0,
             0x0, 0x0), (
                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x4000000, 0x2000000, 0x7700000, 0xfe00000, 0xfc00000,
                0xfe00000,
                0x7f00000, 0x7e00000, 0x3c00000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                0x0,
                0x0, 0x0), (
                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x4000000, 0x2000000, 0x7400000, 0xf800000, 0xf800000,
                0xf800000,
                0x7c00000, 0x7e00000, 0x3c00000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                0x0,
                0x0, 0x0), (
                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x4000000, 0x2000000, 0x7000000, 0xf000000, 0xe000000,
                0xe000000,
                0x7000000, 0x7800000, 0x3c00000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                0x0,
                0x0, 0x0), (
                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x4000000, 0x2000000, 0x1000000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                0x0,
                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0), (
                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                0x0,
                0x0,
                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0))
        OVERLAY_STINK = (
            (0x0, 0x0, 0x0, 0x0, 0x10000000, 0x8000008, 0x10000004, 0xa000028, 0x11000044, 0xa000028, 0x1000044,
             0x12000020, 0x21000040, 0x10000000, 0x20000000, 0x10000000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
             0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0), (
                0x0, 0x0, 0x0, 0x10000000, 0x8000008, 0x10000004, 0xa000028, 0x11000044, 0xa000028, 0x1000044,
                0x12000020, 0x21000040, 0x10000000, 0x20000000, 0x10000000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0))
        OVERLAY_DEAD = ((
                            0x0, 0x0, 0xfc00000, 0x1fe00000, 0x1b600000, 0x1fe00000, 0xfc00000, 0xfc00000, 0x5400000,
                            0x0,
                            0x0,
                            0x0,
                            0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                            0x0,
                            0x0),
                        (
                            0x0, 0x0, 0x7e00000, 0xff00000, 0xdb00000, 0xff00000, 0x7e00000, 0x7e00000, 0x2a00000, 0x0,
                            0x0,
                            0x0,
                            0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                            0x0,
                            0x0))
        OVERLAY_EXCLAIM = ((
                               0x0, 0x20, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x20, 0x0, 0x20, 0x70, 0x20, 0x0,
                               0x0,
                               0x0,
                               0x0,
                               0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0), (
                               0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                               0x0,
                               0x0,
                               0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0))
        OVERLAY_CLEAN = (
            (0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2,
             0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2),)

        PIXEL_COLOR = (10, 12, 6)
        NON_PIXEL_COLOR = (156, 170, 125)

        def __init__(self, screen):
            self.update_game_animation = False
            self.eat_frame_number = 0
            self.death_frame_number = 0
            self.sleep_frame_number = 0
            self.current_anim_offset = None
            self.current_anim_frame_number = 0
            self.creature_image = None
            self.screen = screen
            pygame.time.set_timer(self.UPDATE_ANIMATION_EVENT, self.SECOND)

        @staticmethod
        def get_random_offset():
            return random.randint(-3, 2)

        @staticmethod
        def get_next_frame_number(animation_frames, current_frame_number):
            return (current_frame_number + 1) % len(animation_frames)

        def display_creature_image(self, animations, stage):
            self.creature_image = animations[stage][self.current_anim_frame_number]
            self.current_anim_frame_number = self.get_next_frame_number(animations[stage],
                                                                        self.current_anim_frame_number)

        def overlap_image(self, overlay_anim, frame):
            overlay_image = overlay_anim[frame]
            self.creature_image = self.bit_or(self.creature_image, overlay_image)

        def update_animation(self, current_state, current_transition, stage, stink, exclaim):

            if current_state is CreatureSM.States.IDLE:
                pygame.time.set_timer(self.UPDATE_ANIMATION_EVENT, self.SECOND)
                self.current_anim_offset = self.get_random_offset()
                self.display_creature_image(self.IDLE_ANIMATIONS, stage)
            elif current_state is CreatureSM.States.SLEEP:
                self.current_anim_offset = 0
                self.display_creature_image(self.SLEEP_ANIMATIONS, stage)
                self.overlap_image(self.OVERLAY_ZZZ, self.sleep_frame_number)
                self.sleep_frame_number = self.get_next_frame_number(self.OVERLAY_ZZZ,
                                                                     self.sleep_frame_number)
            elif current_state is CreatureSM.States.DEATH:
                self.current_anim_offset = 3
                self.display_creature_image(self.SLEEP_ANIMATIONS, stage)
                self.overlap_image(self.OVERLAY_DEAD, self.death_frame_number)
                self.death_frame_number = self.get_next_frame_number(self.OVERLAY_DEAD,
                                                                     self.death_frame_number)
            elif current_state is CreatureSM.States.EAT:
                self.display_creature_image(self.IDLE_ANIMATIONS, stage)
                self.overlap_image(self.OVERLAY_EAT, self.eat_frame_number)
                self.eat_frame_number = self.get_next_frame_number(self.OVERLAY_EAT, self.eat_frame_number)
                self.current_anim_offset = self.get_random_offset()
            elif current_state is CreatureSM.States.CLEAN:
                pygame.time.set_timer(self.UPDATE_ANIMATION_EVENT, int(self.SECOND / 10))
                self.current_anim_frame_number = 0
                self.display_creature_image(self.IDLE_ANIMATIONS, stage)
                self.overlap_image(self.OVERLAY_CLEAN, 0)
                self.current_anim_offset -= 1

            if current_state is not CreatureSM.States.DEATH:
                if stink != 0:
                    self.overlap_image(self.OVERLAY_STINK, stink % 2)
                if exclaim != 0:
                    self.overlap_image(self.OVERLAY_EXCLAIM, exclaim % 2)

        def render_main_display(self, invert_colors):
            # Render display
            fg_color = self.PIXEL_COLOR
            bg_color = self.NON_PIXEL_COLOR
            if invert_colors:
                fg_color = self.NON_PIXEL_COLOR
                bg_color = self.PIXEL_COLOR

            self.render_display(self.creature_image, fg_color, bg_color, self.current_anim_offset)

        @staticmethod
        def bit_or(current_frame, overlay_frame):
            l = []
            for i in range(32):
                b = current_frame[i] | overlay_frame[i]
                l.append(b)
            return tuple(l)

        @staticmethod
        def bit_not(current_frame):
            l = []
            for i in range(32):
                b = ~current_frame[i]
                l.append(b)
            return tuple(l)

        @staticmethod
        def get_bits(number, num_bits):
            """Solution from http://stackoverflow.com/questions/16659944/iterate-between-bits-in-a-binary-number"""
            return [(number >> bit) & 1 for bit in range(num_bits - 1, -1, -1)]

        def render_display(self, image_data, fg_color, bg_color, off=0, percv=0):
            if image_data is not None:
                for y in range(32):
                    for x in range(32):
                        pygame.draw.rect(self.screen, fg_color, ((x) * 10 + 32, y * 10 + 64, 8, 8))
                for y in range(32):
                    bits = self.get_bits(image_data[y], 32 + off)
                    bits.reverse()
                    for x in range(off, 32 + off):
                        color = bg_color
                        if x in range(len(bits)):
                            if bits[x] or percv > 0 and y > 11 and x > 2 and y < 17 and x < 3 + percv:
                                color = fg_color
                        pygame.draw.rect(self.screen, color, ((x - off) * 10 + 32, y * 10 + 64, 8, 8))

        def update_animation_event(self):
            for _ in pygame.event.get(self.UPDATE_ANIMATION_EVENT):
                self.update_game_animation = True

    BUTTON_H = 32
    BUTTON_W = 32

    def __init__(self):
        self.mouse_x = 0
        self.mouse_y = 0
        self.curr_cmd = None
        self.eat_image = pygame.transform.scale(pygame.image.load('images/bread.png'),
                                                (self.BUTTON_W, self.BUTTON_H))
        self.clean_image = pygame.transform.scale(pygame.image.load('images/clean.png'),
                                                  (self.BUTTON_W, self.BUTTON_H))
        self.light_image = pygame.transform.scale(pygame.image.load('images/light.png'),
                                                  (self.BUTTON_W, self.BUTTON_H))
        self.select_image = pygame.transform.scale(pygame.image.load('images/select.png'),
                                                   (self.BUTTON_W, self.BUTTON_H))
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 0, 32)
        pygame.display.set_caption('Tamagotchi')
        self.font = pygame.font.SysFont('Arial', 14)

        self.main_display = self.MainDisplay(self.screen)

    def render_main_display(self, invert_colors):
        self.main_display.render_main_display(invert_colors)
        pygame.display.update()
        self.clock.tick(self.FPS)

    def update_animation(self, current_state, current_transition, stage, stink, exclaim):
        if self.main_display.update_game_animation:
            self.main_display.update_animation(current_state, current_transition, stage, stink, exclaim)
            self.main_display.update_game_animation = False

    def render_buttons(self):
        # Render components
        buttons_images = [{'command': TamagotchiEmulator.COMMANDS.EAT, 'image': self.eat_image},
                          {'command': TamagotchiEmulator.COMMANDS.CLEAN, 'image': self.clean_image},
                          {'command': TamagotchiEmulator.COMMANDS.SWITCH_LIGHT, 'image': self.light_image}]

        self.curr_cmd = None
        for i in range(len(buttons_images)):
            button_x = (i + 1) * 64
            button_y = 16
            self.screen.blit(buttons_images[i]['image'], (button_x, button_y))

            button_rect = pygame.Rect(button_x, button_y, self.BUTTON_W, self.BUTTON_H)
            buttons_images[i]['pos'] = (button_x, button_y)
            if button_rect.collidepoint(self.mouse_x, self.mouse_y):
                self.curr_cmd = {'pos': (button_x, button_y), 'command': buttons_images[i]['command']}

        # Render selector
        if self.curr_cmd is not None:
            self.screen.blit(self.select_image,
                             (self.curr_cmd['pos'][0], self.curr_cmd['pos'][1]))

    def render_debug_info(self, debug_info):
        # Render debug
        surf = self.font.render('DEBUG INFO:', True, self.PIXEL_COLOR)
        self.screen.blit(surf, (360, 60))
        debug = (('AGE: %s', 'HUNGER: %s', 'ENERGY: %s', 'WASTE: %d', 'HAPPINESS: %s','STATE: %s', 'TRANSITION: %s'),
                 ('age', 'hunger', 'energy', 'waste', 'happiness', 'state', 'transition'))
        y_pos = 15
        for pos, y in enumerate(i for i in range(0, len(debug_info) * y_pos, y_pos)):
            surf = self.font.render(debug[0][pos] % debug_info[debug[1][pos]], True, self.PIXEL_COLOR)
            self.screen.blit(surf, (360, y+80))

    def clean_screen(self):
        self.screen.fill(self.BG_COLOR)

    def handle_gui_event(self):
        self.mouse_x = 0
        self.mouse_y = 0
        # GUI Event handler
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                self.mouse_x, self.mouse_y = event.pos


if __name__ == '__main__':
    TamagotchiEmulator().main()
