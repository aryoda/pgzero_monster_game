import tiles_engine as engine


class GameLevel:

    # _level_name = ""
    #
    # _game_map = []
    # _tile_images = {}
    #
    # _map_width = 0
    # _map_height = 0
    #
    # _tile_width = 0
    # _tile_height = 0
    #
    # _solid_tiles = ""
    #
    # # Größe der Spielfläche in Pixel
    # _screen_width = 0
    # _screen_heigth = 0


    def __init__(self, game_map_file_name, tiles_file_name, tile_width, tile_height, level_name = ""):

        self._tile_width = tile_width
        self._tile_height = tile_height

        if level_name == "":
            self._level_name = game_map_file_name
        else:
            self._level_name = level_name

        self._game_map = engine.load_game_map(game_map_file_name)

        # Lade Textur-Paket
        # engine.read_tile_images("tile_images.txt", tile_images, TILE_WIDTH, TILE_HEIGHT)
        self._tile_images = engine.load_tile_images(tiles_file_name, self._tile_width, self._tile_height)

        # Breite und Höhe der Karte ermitteln und merken
        self._map_width = len(self._game_map[0])
        self._map_height = len(self._game_map)

        # Fenster-Größe an Map-Größe anpassen
        self._screen_width = self._map_width * self._tile_width
        self._screen_heigth = self._map_height * self._tile_height

        if self._screen_width > 1920 or self._screen_heigth > 1080:
            print("Warnung: Der Spiellevel ist zu groß für einen FullHD-Bildschirm!")

    def get_level_name(self):
        return self._level_name

    def get_game_map(self):
        return self._game_map

    def get_tile_images(self):
        return self._tile_images

    def get_map_width(self):
        return self._map_width

    def get_map_height(self):
        return self._map_height

    def get_tile_width(self):
        return self._tile_width

    def get_tile_height(self):
        return self._tile_height

    def get_solid_tiles(self):
        return self._solid_tiles

    def get_screen_width(self):
        return self._screen_width

    def get_screen_height(self):
        return self._screen_heigth

