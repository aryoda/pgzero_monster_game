# import pgzrun
from pgzero.builtins import Actor, animate, keyboard  # https://github.com/lordmauve/pgzero/issues/61
# import pgzero
import pygame
from random import randint


# Open Source 2D level editor "Tiled":
# https://doc.mapeditor.org/en/stable/manual/introduction/

# Directions:
#      3
#   1  5  2
#      4
move_directions = {
    1: (-1, 0),
    2: (+1, 0),
    3: (0, -1),
    4: (0, +1),
    5: (0, 0)
}
# TODO Use an enum, see:
# https://github.com/lordmauve/pgzero/blob/master/examples/snake/snake.py
# class Direction(Enum):
#     RIGHT = (1, 0)
#     UP = (0, -1)
#     LEFT = (-1, 0)
#     DOWN = (0, 1)
#
#     def opposite(self):
#         x, y = self.value
#         return Direction((-x, -y))
# KEYBINDINGS = {
#     keys.LEFT: Direction.LEFT,
#     keys.RIGHT: Direction.RIGHT,
#     keys.UP: Direction.UP,
#     keys.DOWN: Direction.DOWN,
# }
# def on_key_down(key):
#     dir = KEYBINDINGS.get(key)
#     if dir and dir != snake.lastdir.opposite():
#         snake.dir = dir
#         return
#


def load_game_map(file_name):
    with open(file_name, 'r') as file:
        game_map = file.read().splitlines()

    # if len(map) != height:
    #     print("Error: Zeilenanzahl stimmt nicht! " + str(height) + " vs. " + str(len(map)))

    width = -1

    for line in game_map:
        if width == -1:            # use the first map line as the expected width
            width = len(line)
        elif len(line) != width:
            print("Error: Diese Zeile hat nicht die richtige Breite: " + line)
            print(len(line))

    return game_map


def load_tile_images(file_name, tile_width, tile_height):

    tile_images_dict = {}

    with open(file_name, 'r') as file:
        file_content = file.read().splitlines()

    for line in file_content:
        code_name_pair = line.split("=")
        if len(code_name_pair) != 2:
            print("Error: Ungültige Tile-Image-Zeile: " + image)
        else:
            code = code_name_pair[0]
            image_name = code_name_pair[1]
            tile_image = Actor(code_name_pair[1])
            resize_actor(tile_image, tile_width, tile_height)
            tile_images_dict[code] = tile_image._surf

    return tile_images_dict


def resize_actor(actor, new_width, new_heigth):
    # Resize and update the anchor point
    # See: https://www.pygame.org/docs/ref/transform.html#pygame.transform.scale
    actor._surf = pygame.transform.scale(actor._surf, (new_width, new_heigth))
    actor._update_pos()

    return actor  # nicht benötigter Rückgabewert


def pos_in_map(map_x, map_y, tile_width, tile_height):

    tile_x = map_x // tile_width
    tile_y = map_y // tile_height

    return((tile_x, tile_y))


def pos_as_pixel(map_x, map_y, tile_width, tile_height):

    x = map_x * tile_width
    y = map_y * tile_height

    return((x, y))


def tile_at_pixel(game_map, tile_width, tile_height, x, y):

    map_pos = pos_in_map(x, y, tile_width, tile_height)

    return game_map[map_pos[1]][map_pos[0]]


def tile_at_map_pos(game_map, x, y):

    return game_map[int(y)][int(x)]


def set_tile_at_map_pos(game_map, x, y, tile):

    # Python strings are immutable so you have to create a new string
    line = game_map[y]
    new_line = "".join((line[:x], tile[0], line[x+1:]))
    game_map[y] = new_line


def calc_moved_pos(actor, direction, tile_height, tile_width):

    map_pos = pos_in_map(actor.left, actor.top, tile_width, tile_height)
    offset = move_directions[direction]
    new_map_pos = (map_pos[0] + offset[0], map_pos[1] + offset[1])

    return new_map_pos


def move_actor(actor, direction, tile_height, tile_width, animation_duration = 0):

    map_pos = pos_in_map(actor.left, actor.top, tile_width, tile_height)
    offset = move_directions[direction]

    new_map_pos = (map_pos[0] + offset[0], map_pos[1] + offset[1])
    new_pixel_pos = pos_as_pixel(new_map_pos[0], new_map_pos[1], tile_width, tile_height)

    if animation_duration != 0:
        animate(actor, left=new_pixel_pos[0], top=new_pixel_pos[1], duration=0.7, tween="linear")
    else:
        actor.left = new_map_pos[0] * tile_width
        actor.top = new_map_pos[1] * tile_height


def can_move(actor, direction, game_map, map_width, map_height, tile_width, tile_height, solid_tiles):

    new_pos = calc_moved_pos(actor, direction, tile_height, tile_width)

    # no movement beyond left, right, upper and lower border
    if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] >= map_width or new_pos[1] >= map_height:
        tile = solid_tiles[0]                     # use the first solid tile block the movement direction
    else:
        tile = tile_at_map_pos(game_map, new_pos[0], new_pos[1])

    res = False
    if solid_tiles.find(tile) < 0:
        res = True

    return res


def allowed_directions(actor, game_map, map_width, map_height, tile_width, tile_height, solid_tiles):

    # map_pos = pos_in_map(actor.left, actor.top, tile_width, tile_height)

    res = []

    for direction in range(1, 5):  # Note: Direction 5 (= don't move) is NOT reported as an allowed direction to keep zombies moving
        if can_move(actor, direction, game_map, map_width, map_height, tile_width, tile_height, solid_tiles):
            res.append(direction)

    return res


def find_random_map_pos(game_map, map_width, map_height, player_x, player_y, min_player_distance = 3, allowed_tiles = " "):

    tile = "keine Kachel"

    while allowed_tiles.find(tile) < 0:  # freien Platz in der Game Map gefunden?
        map_x = randint(0, map_width - 1)
        map_y = randint(0, map_height- 1)
        tile = tile_at_map_pos(game_map, map_x, map_y)
        # Mindest-Abstand zur Spielerfigur eingehalten?
        if abs(map_x - player_x) < min_player_distance \
            and abs(map_y - player_y) < min_player_distance:
            tile = "zu nah am Spieler"

    return((map_x, map_y))  # Ergebnis ist ein Tupel


