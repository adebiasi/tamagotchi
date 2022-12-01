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


class CreatureSM(object):
    class CreatureStates(Enum):
        IDLE = 0
        EAT = 1
        CLEAN = 2
        SLEEP = 3
        DEATH = 4

    class CreatureTransitions(Enum):
        IDLE_TO_IDLE = 0
        IDLE_TO_EAT = 1
        EAT_TO_EAT = 2
        EAT_TO_IDLE = 3
        IDLE_TO_CLEAN = 4
        CLEAN_TO_CLEAN = 5
        CLEAN_TO_IDLE = 6
        IDLE_TO_SLEEP = 7
        SLEEP_TO_SLEEP = 8
        SLEEP_TO_IDLE = 9
        IDLE_TO_DEATH = 10

    def __init__(self):
        self.current_state = None
        self.current_transition = None
        self.set_current_state(self.CreatureStates.IDLE)
        self.current_state_counter = 0

    def set_current_state(self, state):
        self.current_state = state
        self.current_state_counter = 0

    def set_current_transition(self, transition):
        print("set_current_transition: " + str(transition))
        self.current_transition = transition

    def current_state_is(self, state):
        return self.current_state is state


class Creature(CreatureSM):
    AGE_HATCH = 8  # changed. prev value: 128
    AGE_MATURE = 96  # changed. prev value: 796
    AGE_DEATHFROMNATURALCAUSES = 192  # changed. prev value: 8192
    HUNGER_CANEAT = 32
    HUNGER_NEEDSTOEAT_LEVEL = 128
    HUNGER_SICKFROMNOTEATING = 256
    HUNGER_DEADFROMNOTEATING_LEVEL = 512
    ENERGY_CANSLEEP = 500  # changed. prev value: 150
    ENERGY_TIRED_LEVEL = 20  # changed. prev value: 64
    ENERGY_PASSOUT = 8
    WASTE_EXPUNGE_LEVEL = 20  # changed. prev value: 256

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


class TamagotchiEmulator:
    if platform.system() == 'Windows':
        os.environ['SDL_VIDEODRIVER'] = 'windib'

    class COMMANDS(Enum):
        NONE = -1
        EAT = 0
        CLEAN = 1
        SWITCH_LIGHT = 3

    def __init__(self):
        self.light = True
        self.creature = Creature()

    def main(self):
        g_interface = GraphicalInterface();

        selid = 0
        curr_command = self.COMMANDS.NONE
        update_game = False

        # Game loop
        while True:
            g_interface.clean_screen()

            # Event handler
            for _ in pygame.event.get(g_interface.UPDATE_GAME_EVENT):
                update_game = True

            g_interface.handle_gui_event()

            if g_interface.curr_cmd is not None:
                curr_command = g_interface.curr_cmd['command']

            # Game logic
            if update_game:
                # evolution phase
                self.creature.handle_evolution()

                # state phase
                if curr_command == self.COMMANDS.SWITCH_LIGHT:
                    self.light = not self.light

                if self.creature.current_state_is(self.creature.CreatureStates.IDLE):
                    self.creature.do_step()

                    if self.creature.stage > 0:
                        if self.light and curr_command == self.COMMANDS.EAT:
                            self.creature.set_current_transition(self.creature.CreatureTransitions.IDLE_TO_EAT)
                            self.creature.set_current_state(self.creature.CreatureStates.EAT)
                            # curr_command = self.COMMANDS.NONE
                        elif self.light and curr_command == self.COMMANDS.CLEAN:
                            self.creature.set_current_transition(self.creature.CreatureTransitions.IDLE_TO_CLEAN)
                            self.creature.set_current_state(self.creature.CreatureStates.CLEAN)
                        elif not self.light and self.creature.status['energy'] <= self.creature.ENERGY_CANSLEEP:
                            self.creature.set_current_transition(self.creature.CreatureTransitions.IDLE_TO_SLEEP)
                            self.creature.set_current_state(self.creature.CreatureStates.SLEEP)
                        elif self.creature.status['energy'] < self.creature.ENERGY_PASSOUT:
                            self.creature.status['happiness'] -= 64
                            self.creature.set_current_transition(self.creature.CreatureTransitions.IDLE_TO_SLEEP)
                            self.creature.set_current_state(self.creature.CreatureStates.SLEEP)
                        elif self.creature.status['hunger'] >= self.creature.HUNGER_DEADFROMNOTEATING_LEVEL or \
                                self.creature.status[
                                    'age'] >= self.creature.AGE_DEATHFROMNATURALCAUSES:
                            self.creature.set_current_transition(self.creature.CreatureTransitions.IDLE_TO_DEATH)
                            self.creature.set_current_state(self.creature.CreatureStates.DEATH)
                elif self.creature.current_state_is(self.creature.CreatureStates.EAT):
                    if self.creature.current_state_counter == 6:
                        self.creature.set_current_transition(self.creature.CreatureTransitions.EAT_TO_IDLE)
                        self.creature.set_current_state(self.creature.CreatureStates.IDLE)
                        self.creature.status['hunger'] = 0
                    else:
                        self.creature.set_current_transition(self.creature.CreatureTransitions.EAT_TO_EAT)
                elif self.creature.current_state_is(self.creature.CreatureStates.SLEEP):
                    if self.creature.status['energy'] >= 256 or self.light:
                        self.creature.set_current_transition(self.creature.CreatureTransitions.SLEEP_TO_IDLE)
                        self.creature.set_current_state(self.creature.CreatureStates.IDLE)
                    else:
                        self.creature.set_current_transition(self.creature.CreatureTransitions.SLEEP_TO_SLEEP)
                        self.creature.status['energy'] += 8
                elif self.creature.current_state_is(self.creature.CreatureStates.CLEAN):
                    if self.creature.current_state_counter == 33:
                        self.creature.set_current_transition(self.creature.CreatureTransitions.CLEAN_TO_IDLE)
                        self.creature.set_current_state(self.creature.CreatureStates.IDLE)
                        self.creature.status['waste'] = 0
                    else:
                        self.creature.set_current_transition(self.creature.CreatureTransitions.CLEAN_TO_CLEAN)
                curr_command = self.COMMANDS.NONE

                # signal phase
                if self.creature.status['waste'] >= self.creature.WASTE_EXPUNGE_LEVEL:
                    self.creature.signals['stink'] += 1
                else:
                    self.creature.signals['stink'] = 0
                if self.creature.status['energy'] <= self.creature.ENERGY_TIRED_LEVEL or self.creature.status[
                    'hunger'] >= self.creature.HUNGER_NEEDSTOEAT_LEVEL \
                        or self.creature.status[
                    'waste'] >= self.creature.WASTE_EXPUNGE_LEVEL - self.creature.WASTE_EXPUNGE_LEVEL / 3:
                    self.creature.signals['exclaim'] += 1
                else:
                    self.creature.signals['exclaim'] = 0

                g_interface.update_animation(self.creature.current_state, self.creature.current_transition,
                                             self.creature.stage, self.creature.signals['stink'],
                                             self.creature.signals['exclaim'],self.light)

                update_game = False
                self.creature.current_state_counter += 1

            g_interface.render_main_display()
            g_interface.render(self.creature.status)


class GraphicalInterface:
    UPDATE_GAME_EVENT = USEREVENT + 1
    SECOND = 1000

    FPS = 30
    SCREEN_WIDTH = 500
    SCREEN_HEIGHT = 520

    # Colors
    BG_COLOR = (160, 178, 129)
    PIXEL_COLOR = (10, 12, 6)
    NON_PIXEL_COLOR = (156, 170, 125)
    TRANSPARENT_COLOR = (0, 0, 0, 0)
    BTN_BORDER_COLOR = (128, 12, 24)
    BTN_CENTER_COLOR = (200, 33, 44)

    class Animations:
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
    ZZZ = (
        0x0, 0x0, 0x0, 0x0, 0xf800000, 0x4000000, 0x2000000, 0x1000000, 0xf800000, 0x0, 0x0, 0x3c00000, 0x1000000,
        0x800000,
        0x3c00000, 0x0, 0x700000, 0x200000, 0x700000, 0x0, 0x80000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0)

    def __init__(self):
        # global screen, clock
        self.eat_frame_number = 0
        self.death_frame_number = 0
        self.sleep_frame_number = 0
        self.current_anim_offset = None
        self.current_anim_frame_number = 0
        self.curr_cmd = None
        self.creature_image = None
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

    @staticmethod
    def get_random_offset():
        return random.randint(-3, 2)

    @staticmethod
    def get_next_frame_number(animation_frames, current_frame_number):
        return (current_frame_number + 1) % len(animation_frames)

    def display_creature_image(self, animations, stage):
        self.creature_image = animations[stage][self.current_anim_frame_number]
        self.current_anim_frame_number = self.get_next_frame_number(animations[stage], self.current_anim_frame_number)

    def overlap_image(self,overlay_anim, frame):
        overlay_image = overlay_anim[frame]
        self.creature_image = GraphicalInterface.bitor(self.creature_image, overlay_image)

    def update_animation(self, current_state, current_transition, stage, stink, exclaim, light):

        print("current_state: " + str(current_state))
        print("current_transition: " + str(current_transition))
        print("stage: " + str(stage))

        if current_state is CreatureSM.CreatureStates.IDLE:
            pygame.time.set_timer(self.UPDATE_GAME_EVENT, self.SECOND)
            self.current_anim_offset = self.get_random_offset()
            self.display_creature_image(self.Animations.IDLE_ANIMATIONS, stage)
        elif current_state is CreatureSM.CreatureStates.SLEEP:
            self.current_anim_offset = 0
            self.display_creature_image(self.Animations.SLEEP_ANIMATIONS, stage)
            self.overlap_image(self.Animations.OVERLAY_ZZZ,self.sleep_frame_number)
            self.sleep_frame_number = self.get_next_frame_number(self.Animations.OVERLAY_ZZZ, self.sleep_frame_number)
        elif current_state is CreatureSM.CreatureStates.DEATH:
            self.current_anim_offset = 3
            self.display_creature_image(self.Animations.SLEEP_ANIMATIONS, stage)
            self.overlap_image(self.Animations.OVERLAY_DEAD, self.death_frame_number)
            self.death_frame_number = self.get_next_frame_number(self.Animations.OVERLAY_DEAD, self.death_frame_number)
        elif current_state is CreatureSM.CreatureStates.EAT:
            self.display_creature_image(self.Animations.IDLE_ANIMATIONS, stage)
            self.overlap_image(self.Animations.OVERLAY_EAT, self.eat_frame_number)
            self.eat_frame_number = self.get_next_frame_number(self.Animations.OVERLAY_EAT, self.eat_frame_number)
            self.current_anim_offset = self.get_random_offset()
        elif current_state is CreatureSM.CreatureStates.CLEAN:
            pygame.time.set_timer(self.UPDATE_GAME_EVENT, int(self.SECOND / 10))
            self.current_anim_frame_number = 0
            self.display_creature_image(self.Animations.IDLE_ANIMATIONS, stage)
            self.overlap_image(self.Animations.OVERLAY_CLEAN, 0)
            self.current_anim_offset -= 1

        if stink != 0:
            self.overlap_image(self.Animations.OVERLAY_STINK, stink%2)

        if exclaim != 0:
            self.overlap_image(self.Animations.OVERLAY_EXCLAIM, exclaim%2)

        if not light:
            self.creature_image = GraphicalInterface.bitnot(self.creature_image)

    def render_main_display(self):
        # Render display
        if self.creature_image is not None:
            self.render_display(self.creature_image, self.PIXEL_COLOR, self.NON_PIXEL_COLOR, self.current_anim_offset)

    def render(self, pet):

        # Render components
        buttons_images = [{'command': TamagotchiEmulator.COMMANDS.EAT, 'image': self.FEED},
                          {'command': TamagotchiEmulator.COMMANDS.CLEAN, 'image': self.FLUSH},
                          # {'command': TamagotchiEmulator.COMMANDS.NONE, 'image': self.HEALTH},
                          {'command': TamagotchiEmulator.COMMANDS.SWITCH_LIGHT, 'image': self.ZZZ}]

        self.curr_cmd = None
        for i in range(len(buttons_images)):
            button_h = 32
            button_w = 32
            button_surface = pygame.Surface((button_w, button_h))
            GraphicalInterface.render_component(button_surface, buttons_images[i]['image'], self.PIXEL_COLOR,
                                                self.NON_PIXEL_COLOR)
            button_x = (i + 1) * 64
            button_y = 16
            buttons_images[i]['rect'] = pygame.Rect(button_x, button_y, button_w, button_h)
            buttons_images[i]['pos'] = (button_x, button_y)
            if buttons_images[i]['rect'].collidepoint(self.mouse_x, self.mouse_y):
                self.curr_cmd = buttons_images[i]

            self.screen.blit(pygame.transform.flip(button_surface, True, False), (button_x, button_y))

        # Render selector
        if self.curr_cmd is not None:
            self.screen.blit(pygame.transform.flip(self.selector_img, True, False),
                             (self.curr_cmd['pos'][0], self.curr_cmd['pos'][1]))

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

    @staticmethod
    def bitor(current_frame, overlay_frame):
        l = []
        for i in range(32):
            b = current_frame[i] | overlay_frame[i]
            l.append(b)
        return tuple(l)

    @staticmethod
    def bitnot(current_frame):
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
        # self.overlay_anim = None

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
