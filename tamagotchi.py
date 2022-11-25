# Tamagotchi - A port of the Tamagotchi Emulator by aerospark: https://goo.gl/gaZ1fA            
# Copyright (C) 2017 Ryan Salvador

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
from IPython.lib.display import Code
from pygame.locals import *


class Creature:
    AGE_HATCH = 8  # changed. prev value: 128
    AGE_MATURE = 796
    AGE_DEATHFROMNATURALCAUSES = 8192
    HUNGER_CANEAT = 32
    HUNGER_NEEDSTOEAT_LEVEL = 128
    HUNGER_SICKFROMNOTEATING = 256
    HUNGER_DEADFROMNOTEATING_LEVEL = 512
    ENERGY_CANSLEEP = 150
    ENERGY_TIRED_LEVEL = 64
    ENERGY_PASSOUT = 8
    WASTE_EXPUNGE_LEVEL = 256

    class CREATURE_STATES(Enum):
        IDLE = 0
        EAT = 1
        CLEAN = 2
        SLEEP = 3
        DEATH = 4

    def __init__(self):
        self.current_state_counter = 0
        self.set_current_state(self.CREATURE_STATES.IDLE)
        self.pet = {'hunger': 0, 'energy': 256, 'waste': 0, 'age': 0, 'happiness': 0}
        self.stage = 0

    def set_current_state(self, state):
        self.current_state_counter = 0
        self.current_state = state

    def handle_evolution(self):
        if self.stage == 0 and self.pet['age'] > self.AGE_HATCH:
            print("evolving")
            self.stage += 1
            self.set_current_state(self.current_state)
        if self.stage == 1 and self.pet['age'] > self.AGE_MATURE:
            print("evolving")
            self.stage += 1
            self.set_current_state(self.current_state)

    def do_random_event(self):
        num = random.randint(0, 31)
        if num == 12:
            self.pet['hunger'] += 1
        elif num == 16:
            self.pet['energy'] -= 1
        elif num == 18:
            self.pet['energy'] += 1
        elif num == 20:
            self.pet['waste'] += 1
        elif num == 7:
            self.pet['happiness'] += 1
        elif num == 4:
            self.pet['happiness'] -= 1

    def do_cycle(self):
        self.do_random_event()
        self.pet['hunger'] += 1
        self.pet['waste'] += 1
        self.pet['energy'] -= 1
        self.pet['age'] += 2
        if self.pet['waste'] >= self.WASTE_EXPUNGE_LEVEL:
            self.pet['happiness'] -= 1


class TamagotchiEmulator:
    if platform.system() == 'Windows':
        os.environ['SDL_VIDEODRIVER'] = 'windib'

    # Animations
    IDLE_EGG = ((0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7e000,
                 0x87000, 0x103800, 0x300c00, 0x700400, 0x418200, 0x418200, 0x400200, 0x700600, 0x3c0c00, 0x1e0800,
                 0x3ffc00, 0x0), (
                    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                    0x7e000,
                    0x87000, 0x103800, 0x300c00, 0x700400, 0x400200, 0x418200, 0x418200, 0x700600, 0x3c0c00, 0xffff00,
                    0x0))
    IDLE_BABY = (
        (0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
         0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x78000, 0xb4000, 0x1fe000), (
            0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
            0x0,
            0x0, 0x0, 0x0, 0x0, 0x78000, 0xcc000, 0x84000, 0xb4000, 0x84000, 0x78000, 0x0))
    IDLE_MATURE = ((0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xfc00, 0x10200, 0x24900, 0x20100, 0x23100, 0x20100,
                    0x20100, 0x10200, 0xfc00, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0), (
                       0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xfc00, 0x10200, 0x28500, 0x23100,
                       0x23100,
                       0x20100, 0x10200, 0xfc00, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0))
    SLEEP_BABY = (
        (0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
         0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x78000, 0xfc000, 0x1fe000), (
            0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
            0x0,
            0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1fe000, 0x3ff000))
    SLEEP_MATURE = ((
                        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                        0x0,
                        0x0,
                        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3fc00, 0x40200, 0x80100), (
                        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                        0x0,
                        0x0,
                        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1f800, 0x20400, 0x40200, 0x40200))
    OVERLAY_ZZZ = ((0x0, 0x0, 0x0, 0x0, 0xf800000, 0x4000000, 0x2000000, 0x1000000, 0xf800000, 0x0, 0x0, 0x3c00000,
                    0x1000000, 0x800000, 0x3c00000, 0x0, 0x700000, 0x200000, 0x700000, 0x0, 0x80000, 0x0, 0x0, 0x0, 0x0,
                    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0), (
                       0x0, 0x0, 0x0, 0xf800000, 0x4000000, 0x2000000, 0x1000000, 0xf800000, 0x0, 0x0, 0x3c00000,
                       0x1000000,
                       0x800000, 0x3c00000, 0x0, 0x700000, 0x200000, 0x700000, 0x0, 0x80000, 0x0, 0x0, 0x0, 0x0, 0x0,
                       0x0,
                       0x0,
                       0x0, 0x0, 0x0, 0x0, 0x0))
    OVERLAY_EAT = ((0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x4000000, 0x2000000, 0x7700000, 0xff00000, 0xfd00000, 0xff00000,
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
                        0x0, 0x0, 0xfc00000, 0x1fe00000, 0x1b600000, 0x1fe00000, 0xfc00000, 0xfc00000, 0x5400000, 0x0,
                        0x0,
                        0x0,
                        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                        0x0),
                    (
                        0x0, 0x0, 0x7e00000, 0xff00000, 0xdb00000, 0xff00000, 0x7e00000, 0x7e00000, 0x2a00000, 0x0, 0x0,
                        0x0,
                        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                        0x0))
    OVERLAY_EXCLAIM = ((
                           0x0, 0x20, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x70, 0x20, 0x0, 0x20, 0x70, 0x20, 0x0, 0x0,
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

    class COMMANDS(Enum):
        NONE = -1
        EAT = 0
        CLEAN = 1
        SLEEP = 3

    def __init__(self):
        self.creature = Creature()

    @staticmethod
    def get_random_offset():
        return random.randint(-3, 2)

    @staticmethod
    def get_next_frame(animation_frames, current_frame):
        return (current_frame + 1) % len(animation_frames)

    def trigger_death_animation(self, stage):
        print("trigger_death")
        if stage == 1:
            current_anim = self.SLEEP_BABY
        elif stage == 2:
            current_anim = self.SLEEP_MATURE
        overlay_anim = self.OVERLAY_DEAD
        return current_anim, overlay_anim, True

    def trigger_idle_animation(self, stage):
        has_overlay = False
        if stage == 0:
            current_anim = self.IDLE_EGG
        elif stage == 1:
            current_anim = self.IDLE_BABY
        elif stage == 2:
            current_anim = self.IDLE_MATURE
        return current_anim, has_overlay

    def trigger_sleep_animation(self, stage):
        print("trigger_sleep")
        has_overlay = True
        if stage == 1:
            current_anim = self.SLEEP_BABY
        elif stage == 2:
            current_anim = self.SLEEP_MATURE
        overlay_anim = self.OVERLAY_ZZZ
        return current_anim, overlay_anim, has_overlay

    def trigger_clean_animation(self):
        print("trigger_clean")
        has_overlay = True
        return 0, self.OVERLAY_CLEAN, has_overlay

    def trigger_eat_animation(self):
        print("trigger_eat")
        has_overlay = True
        return 0, self.OVERLAY_EAT, has_overlay

    def main(self):
        g_interface = GraphicalInterface();

        # Tamagotchi

        # Counters
        anim_offset = 0
        selid = 0

        anim_frame = 0
        overlay_frame = 0

        # Flags
        has_overlay = False
        update_game = False

        current_anim = self.IDLE_EGG
        overlay_anim = self.OVERLAY_ZZZ

        # self.current_state_counter = 0

        # Game loop
        while True:
            g_interface.clean_screen()

            # Event handler
            for _ in pygame.event.get(g_interface.UPDATE_GAME_EVENT):
                update_game = True

            g_interface.handle_gui_event()
            # Buttons logic
            curr_command, new_selid = g_interface.get_command()

            if new_selid != -1:
                selid = new_selid
                print(str(curr_command))

            if self.creature.stage > 0:
                if curr_command == self.COMMANDS.EAT:
                    self.creature.set_current_state(self.creature.CREATURE_STATES.EAT)
                elif curr_command == self.COMMANDS.CLEAN:
                    self.creature.set_current_state(self.creature.CREATURE_STATES.CLEAN)
                elif curr_command == self.COMMANDS.SLEEP:
                    if self.creature.pet['energy'] <= self.ENERGY_CANSLEEP:
                        self.creature.set_current_state(self.creature.CREATURE_STATES.SLEEP)

            # Game logic
            if update_game:
                self.creature.handle_evolution()
                if self.creature.current_state == self.creature.CREATURE_STATES.IDLE:
                    pass
                if self.creature.current_state == self.creature.CREATURE_STATES.EAT:
                    print(len(overlay_anim))
                    if self.creature.current_state_counter == 5:
                        print("eat finish")
                        self.creature.set_current_state(self.creature.CREATURE_STATES.IDLE)
                        self.creature.pet['hunger'] = 0
                elif self.creature.current_state == self.creature.CREATURE_STATES.SLEEP:
                    print("sleeping")
                    self.creature.pet['energy'] += 8
                    if self.creature.pet['energy'] >= 256:
                        print("sleep finish")
                        self.creature.set_current_state(self.creature.CREATURE_STATES.IDLE)
                elif self.creature.current_state == self.creature.CREATURE_STATES.CLEAN:
                    print("cleaninig")
                    if self.creature.current_state_counter == 33:
                        print("clean finish")
                        self.creature.set_current_state(self.creature.CREATURE_STATES.IDLE)
                        self.creature.pet['waste'] = 0

                if self.creature.current_state == self.creature.CREATURE_STATES.IDLE:
                    print("do_cycle")
                    self.creature.do_cycle()
                if self.creature.pet['energy'] < self.creature.ENERGY_PASSOUT:
                    if self.creature.stage > 0:
                        self.creature.pet['happiness'] -= 64
                    self.creature.set_current_state(self.creature.CREATURE_STATES.SLEEP)
                    # current_anim, overlay_anim, has_overlay = self.trigger_sleep_animation(stage)
                if self.creature.pet['hunger'] >= self.creature.HUNGER_DEADFROMNOTEATING_LEVEL or self.creature.pet[
                    'age'] >= self.creature.AGE_DEATHFROMNATURALCAUSES:
                    self.creature.set_current_state(self.creature.CREATURE_STATES.DEATH)

                if self.creature.current_state != self.creature.CREATURE_STATES.DEATH:
                    if self.creature.current_state == self.creature.CREATURE_STATES.CLEAN:
                        anim_offset -= 1
                    else:
                        anim_frame = self.get_next_frame(current_anim, anim_frame)
                        anim_offset = self.get_random_offset()
                if self.creature.current_state == self.creature.CREATURE_STATES.IDLE and self.creature.current_state_counter == 0:
                    pygame.time.set_timer(g_interface.UPDATE_GAME_EVENT, g_interface.SECOND)
                    current_anim, has_overlay = self.trigger_idle_animation(self.creature.stage)
                elif self.creature.current_state == self.creature.CREATURE_STATES.SLEEP and self.creature.current_state_counter == 0:
                    current_anim, overlay_anim, has_overlay = self.trigger_sleep_animation(self.creature.stage)
                elif self.creature.current_state == self.creature.CREATURE_STATES.DEATH and self.creature.current_state_counter == 0:
                    anim_offset = 3
                    current_anim, overlay_anim, has_overlay = self.trigger_death_animation(self.creature.stage)
                elif self.creature.current_state == self.creature.CREATURE_STATES.EAT and self.creature.current_state_counter == 0:
                    overlay_frame, overlay_anim, has_overlay = self.trigger_eat_animation()
                elif self.creature.current_state == self.creature.CREATURE_STATES.CLEAN and self.creature.current_state_counter == 0:
                    anim_offset = 0
                    pygame.time.set_timer(g_interface.UPDATE_GAME_EVENT, int(g_interface.SECOND / 10))
                    overlay_frame, overlay_anim, has_overlay = self.trigger_clean_animation()

                if self.creature.current_state == self.creature.CREATURE_STATES.IDLE:
                    if self.creature.pet['waste'] >= self.creature.WASTE_EXPUNGE_LEVEL:
                        overlay_anim = self.OVERLAY_STINK
                        has_overlay = True
                    elif self.creature.pet['energy'] <= self.creature.ENERGY_TIRED_LEVEL or self.creature.pet[
                        'hunger'] >= self.creature.HUNGER_NEEDSTOEAT_LEVEL \
                            or self.creature.pet['waste'] >= self.creature.WASTE_EXPUNGE_LEVEL - self.creature.WASTE_EXPUNGE_LEVEL / 3:
                        overlay_anim = self.creature.OVERLAY_EXCLAIM
                        has_overlay = True

                if has_overlay:
                    print("has overlay: " + str(overlay_frame))
                    overlay_frame = self.get_next_frame(overlay_anim, overlay_frame)
                    print("next overlay_frame: " + str(overlay_frame))
                update_game = False
                self.creature.current_state_counter += 1
            g_interface.render(current_anim, anim_frame, has_overlay, anim_offset, overlay_frame, overlay_anim,
                               self.creature.pet,
                               selid)


class GraphicalInterface:
    UPDATE_GAME_EVENT = USEREVENT + 1
    SECOND = 1000

    FPS = 30
    SCREEN_WIDTH = 500
    SCREEN_HEIGHT = 520

    # Colors
    BG_COLOR = (160, 178, 129)
    PIXEL_COLOR = (10, 12, 6)
    NONPIXEL_COLOR = (156, 170, 125)
    TRANSPARENT_COLOR = (0, 0, 0, 0)
    BTN_BORDER_COLOR = (128, 12, 24)
    BTN_CENTER_COLOR = (200, 33, 44)

    # Components
    SELECTOR = (
        0x7800000f, 0x60000003, 0x40000001, 0x40000001, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x40000001, 0x40000001, 0x60000003, 0x7800000f)
    FEED = (
        0x0, 0x0, 0x0, 0x0, 0x0, 0x7805a0, 0x7c05a0, 0x7c05a0, 0x7c05a0, 0x7c05a0, 0x7c05a0, 0x7c05a0, 0x7c07e0,
        0x7c07e0,
        0x7803c0, 0x7803c0, 0x7803c0, 0x7803c0, 0x7803c0, 0x7803c0, 0x7803c0, 0x7803c0, 0x7803c0, 0x7803c0, 0x7803c0,
        0x7803c0,
        0x7803c0, 0x7803c0, 0x300180, 0x0, 0x0, 0x0)
    FLUSH = (
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x2000000, 0x5000000, 0x5000000, 0x4800000, 0x4800000, 0x4400000, 0x4400000,
        0x4400000, 0x2200000, 0x2200000, 0x1200000, 0xffff00, 0x1200280, 0x11ffd00, 0x1000080, 0x1000080, 0x1000080,
        0x1000080, 0x1000080, 0x1000080, 0x1000040, 0xffff80, 0x0, 0x0, 0x0)
    HEALTH = (
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3ffffc0, 0xc000030, 0x10912488,
        0x10912488,
        0x10492908, 0x8000010, 0x8000010, 0x8000410, 0x4000820, 0x4001020, 0x4002020, 0x201c040, 0x201c040, 0x1ffff80,
        0x0,
        0x0,
        0x0)
    ZZZ = (
        0x0, 0x0, 0x0, 0x0, 0xf800000, 0x4000000, 0x2000000, 0x1000000, 0xf800000, 0x0, 0x0, 0x3c00000, 0x1000000,
        0x800000,
        0x3c00000, 0x0, 0x700000, 0x200000, 0x700000, 0x0, 0x80000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0)
    DISPLAY_HUNGER = (
        0x0, 0x0, 0x3bcc94a4, 0x4852b4a4, 0x39c2d4bc, 0x485a94a4, 0x4bdc9324, 0x0, 0x0, 0x0, 0x0, 0x1ffffff8,
        0x20000004,
        0x20000004, 0x20000004, 0x20000004, 0x20000004, 0x1ffffff8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0,
        0x0,
        0x0, 0x0)
    DISPLAY_ENERGY = (
        0x0, 0x0, 0x498ef4bc, 0x4a521584, 0x704e368c, 0x43521484, 0x3b92f4bc, 0x0, 0x0, 0x0, 0x0, 0x1ffffff8,
        0x20000004,
        0x20000004, 0x20000004, 0x20000004, 0x20000004, 0x1ffffff8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0,
        0x0,
        0x0, 0x0)
    DISPLAY_WASTE = (
        0x0, 0x0, 0x7df38e44, 0x4405144, 0x1c439f44, 0x4441154, 0x7c439128, 0x0, 0x0, 0x0, 0x0, 0x1ffffff8, 0x20000004,
        0x20000004, 0x20000004, 0x20000004, 0x20000004, 0x1ffffff8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0,
        0x0,
        0x0, 0x0)
    DISPLAY_AGE = (
        0x0, 0x0, 0x7ce38, 0x5144, 0x1c17c, 0x5944, 0x7de44, 0x0, 0x0, 0x0, 0x0, 0x1ffffff8, 0x20000004, 0x20000004,
        0x20000004,
        0x20000004, 0x20000004, 0x1ffffff8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0)
    DISPLAY_BACK = (
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x498c710, 0x2a52918, 0x185e77c, 0x2a52918, 0x4992710,
        0x0,
        0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0)

    def __init__(self):
        # global screen, clock
        self.mouse_x = 0
        self.mouse_y = 0
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 0, 32)
        pygame.display.set_caption('Tamagotchi')
        self.font = pygame.font.SysFont('Arial', 14)
        self.selector_img = pygame.Surface((32, 32)).convert_alpha()
        GraphicalInterface.render_component(self.selector_img, self.SELECTOR, self.PIXEL_COLOR, self.TRANSPARENT_COLOR)
        pygame.time.set_timer(self.UPDATE_GAME_EVENT, self.SECOND)

    def render(self, current_anim, frame, has_overlay, off, ol_frame, overlay_anim, pet,
               selector_id):

        # Render components
        zipped = zip([self.FEED, self.FLUSH, self.HEALTH, self.ZZZ], [i for i in range(64, 320, 64)])
        z = list(zipped)
        for i in range(len(z)):
            img = pygame.Surface((32, 32))
            GraphicalInterface.render_component(img, z[i][0], self.PIXEL_COLOR, self.NONPIXEL_COLOR)
            self.screen.blit(pygame.transform.flip(img, True, False), (z[i][1], 16))

        # Render selector
        self.screen.blit(pygame.transform.flip(self.selector_img, True, False), (64 + (selector_id * 64), 16))

        # Render display
        if has_overlay:
            animation = GraphicalInterface.bitor(current_anim[frame], overlay_anim[ol_frame])
        else:
            animation = current_anim[frame]
        self.render_display(animation, self.PIXEL_COLOR, self.NONPIXEL_COLOR, off)

        # Render debug
        surf = self.font.render('DEBUG --', True, self.PIXEL_COLOR)
        self.screen.blit(surf, (360, 60))
        debug = (('AGE: %s', 'HUNGER: %s', 'ENERGY: %s', 'WASTE: %d', 'HAPPINESS: %s'), \
                 ('age', 'hunger', 'energy', 'waste', 'happiness'))
        for pos, y in enumerate(i for i in range(70, 120, 10)):
            surf = self.font.render(debug[0][pos] % pet[debug[1][pos]], True, self.PIXEL_COLOR)
            self.screen.blit(surf, (360, y))
        pygame.display.update()
        self.clock.tick(self.FPS)

    def get_command(self):
        if 18 < self.mouse_y < 48:
            button = 0
            for i in range(0, 64 * 4, 64):
                if 64 + i < self.mouse_x < 97 + i:
                    return TamagotchiEmulator.COMMANDS(button), button
                else:
                    button += 1

        return TamagotchiEmulator.COMMANDS.NONE, -1

    @staticmethod
    def bitor(current_frame, overlay_frame):
        l = []
        for i in range(32):
            b = current_frame[i] | overlay_frame[i]
            l.append(b)
        return tuple(l)

    @staticmethod
    def get_bits(number, num_bits):
        """Solution from http://stackoverflow.com/questions/16659944/iterate-between-bits-in-a-binary-number"""
        return [(number >> bit) & 1 for bit in range(num_bits - 1, -1, -1)]

    def render_display(self, image_data, fg_color, bg_color, off=0, percv=0):
        for y in range(32):
            bits = GraphicalInterface.get_bits(image_data[y], 32 + off)
            bits.reverse()
            for x in range(off, 32 + off):
                color = bg_color
                if x in range(len(bits)):
                    if bits[x] or percv > 0 and y > 11 and x > 2 and y < 17 and x < 3 + percv:
                        color = fg_color
                pygame.draw.rect(self.screen, color, ((x - off) * 10 + 32, y * 10 + 64, 8, 8))

    @staticmethod
    def render_component(surface, image_data, fg_color, bg_color=(255, 255, 255)):
        pixels = pygame.PixelArray(surface)
        for y in range(surface.get_height()):
            bits = GraphicalInterface.get_bits(image_data[y], surface.get_width())
            for x, bit in enumerate(bits):
                if bit:
                    pixels[x][y] = fg_color
                else:
                    pixels[x][y] = bg_color
        del pixels

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
