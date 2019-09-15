from pgzero.builtins import Actor, keys
from time import time

import tiles_engine as engine
# import highscores as hs
import game_level as gl


class Game:

    # die möglichen Spiel-Zustände werden über TRUE/FALSE-Flags verwaltet
    # TODO Enum-Klasse verwenden (z. B. class GameStates(Flag)):
    #      https://docs.python.org/3/library/enum.html
    # started: bool = False  # Flag, ob das Spiel schon läuft
    # game_over: bool = False  # Flag, ob das Spiel zuende ist
    # level_completed = False  # Flag, ob der Level (erfolgreich) beendet wurde
    #
    # _levels = []
    #
    # _player: Actor
    #
    # _zombies = []  # Liste mit den Zombie-Actors
    # _zombie_directions = []  # Liste mit den Richtungen, in welche die Zombies der "zombies"-Liste gerade laufen
    #
    # _move_interval = 0.6  # set in start_level()
    # _start_time = time()
    # _remaining_time = 0
    # _time_limit = 0  # hier nur deklariert, wird beim Spielstart gesetzt
    # _score = 0
    #
    # _username = ""  # global variable with default value (if you don't put name)
    #
    # _tile_width = 0
    # _tile_height = 0


    # level_files - eine Liste von Tupeln mit den Elementen "game map file name" und "tiles file name"
    def __init__(self, level_files, tile_width, tile_height):

        self._tile_width = tile_width
        self._tile_height = tile_height

        self._levels = []

        for game_map_file_name, tiles_file_name in level_files:
            level = gl.GameLevel(game_map_file_name, tiles_file_name, tile_width, tile_height, level_name = game_map_file_name)
            self._levels.append(level)


    # ermittelt die max. Pixelanzahl anhand des größten Levels
    def get_required_screen_width(self):

        width = 100

        for level in self._levels:
            width = max(width, level.get_screen_width())

        return width


    # ermittelt die max. Pixelanzahl anhand des größten Levels
    def get_required_screen_height(self):

        height = 100

        for level in self._levels:
            height = max(height, level.get_screen_height())

        return height


    def init_level(self, level_number):

        global WIDTH
        global HEIGHT

        self.started = False

        if level_number > len(self._levels):
            level_number = len(self._levels)

        level = self._levels[level_number]

        # Fenster-Größe an Map-Größe anpassen
        # TODO Full Screen geht so wieder verloren (mit langer Umschaltzeit in den Fenster-Modus)
        WIDTH = level.get_screen_width()
        HEIGHT = level.get_screen_height()

        # WEITER AB HIER mit dem Refactoring: Eigene Actor-Subklasse verwenden ---------------------------------------------------

        player = Actor("player_dummy")  # erstellt Actor mit fest verdrahtetem player image, da nur so das Image aus den Tiles gesetzt werden kann
        player._surf = level.get_tile_images()["P"]  # Player Image wird auch aus "Textur-Paket" geholt
        engine.resize_actor(player, level.get_tile_width(), level.get_tile_height())
        player_pos = engine.pos_as_pixel(1, 1, level.get_tile_width(), level.get_tile_height())
        player.left = player_pos[0]
        player.top = player_pos[1]

        generate_monsters(level * 2)
        # generate_monsters(100)  # TEST