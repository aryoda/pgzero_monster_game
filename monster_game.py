import pgzero
import pgzrun
import pygame
from random import randint
from time import time
import os
from pgzero.builtins import Actor, keys
import tkinter as tk

# from pgzero.game import PGZeroGame
# from pygame.surface import Surface

import tiles_engine as engine
import highscores as hs
import game as g
import game_level as gl


# pycharm online help:
# https://www.jetbrains.com/help/pycharm/python-code-insight.html

# TODO mapeditor als Level-Designer einsetzbar?
# https://doc.mapeditor.org/en/stable/manual/introduction/


# TODO Bug beheben: Highscore wird manchmal zweimal abgefragt oder gespeichert


# pgzero intro auf Deutsch:
# http://blog.schockwellenreiter.de/2019/03/2019031703.html
# Sidescrolling Game:
# http://blog.schockwellenreiter.de/2019/07/2019070102.html
# Invaders Game mit komplexerer Struktur (mehrere Dateien und mit Klassen!!!)
# http://blog.schockwellenreiter.de/2019/07/2019070701.html
# https://www.raspberrypi.org/magpi/pygame-zero-invaders/
#
# PyGame Video-Tutorials !!!
# https://www.youtube.com/watch?v=nGufy7weyGY&list=PLsk-HSGFjnaH5yghzu7PcOzm9NhsW0Urw&index=4

TITLE = "Monster Game"

TILE_WIDTH  = 50
TILE_HEIGHT = 50

MAP_WIDTH = 0
MAP_HEIGHT = 0  # wird später von initialize_level() berechnet

# Karten-Breite und -Höhe (wird nach dem Laden einer Karte automatisch gesetzt
# MAP_WIDTH  = 0
# MAP_HEIGHT = 0

os.environ['SDL_VIDEO_CENTERED'] = '1'

level = 1    # aktuelle Level-Nummer

MAX_HIGHSCORE_ENTRIES = 10   # Konstante für maximale Anzahl der Highscore-Einträge
HIGHSCORE_FILE_NAME = "highscores.json"

level_files = [
    ("game_map_1.txt", "tile_images_1.txt"),
    ("game_map_2.txt", "tile_images_2.txt"),
    ("game_map_3.txt", "tile_images_3.txt"),
    ("game_map_4.txt", "tile_images_4.txt"),
    ("game_map_5.txt", "tile_images_5.txt"),
    ("game_map_6.txt", "tile_images_6.txt"),
    ("game_map_7.txt", "tile_images_7.txt"),
    ("game_map_8.txt", "tile_images_8.txt"),
    ("game_map_9.txt", "tile_images_9.txt"),
    ("game_map_11.txt", "tile_images_11.txt"),
    ("game_map_10.txt", "tile_images_10.txt"),
    ("game_map_m_2.txt", "tile_images_m_2.txt")
]

game_map = []     # enthält das 2D-Gitternetz ("map") mit den einzelnen Bild-Kacheln ("tiles")

tile_images = {}   # dictionary! key = Buchstabe aus map-Zelle, value = Bild ("image"), das gezeichnet werden soll

player: Actor

monsters = []       # Liste mit den Monster-Actors
monster_directions = []  # Liste mit den Richtungen, in welche die Monster der "monsters"-Liste gerade laufen



# mögliche Spiel-Zustände
started: bool = False     # Flag, ob das Spiel schon läuft
game_over: bool = False   # Flag
level_completed = False

move_interval = 0.6       # set in start_level()
start_time = time()
remaining_time = 0
time_limit = 0            # hier nur deklariert, wird beim Spielstart gesetzt
score = 0

username = ""  # global variable with default value (if you don't put name)


def ask_username():
    global username

    root = tk.Tk()
    root.wm_title("Highscore")

    name_label = tk.Label(root, text = "Enter your name: ")
    name_label.pack()

    name_entry = tk.Entry(root)
    name_entry.pack(side='left')

    def ok_clicked():
        global username

        username = name_entry.get()

        root.destroy()

    b = tk.Button(root, text = 'OK', command = ok_clicked)  # , command=close)
    b.pack(side='right')

    # Center the window as good as possible
    # HACK: https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter

    # Apparently a common hack to get the window size. Temporarily hide the
    # window to avoid update_idletasks() drawing the window in the wrong
    # position.
    root.withdraw()
    root.update_idletasks()  # Update "requested size" from geometry manager

    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    root.geometry("+%d+%d" % (x, y))

    # This seems to draw the window frame immediately, so only call deiconify()
    # after setting correct window position
    root.deiconify()

    root.mainloop()

    if username == "":
        username = "(unknown)"

    return username


def generate_monsters(num_monsters):

    global monsters
    global monster_directions

    monsters = []
    monster_directions = []

    for i in range(0, num_monsters):
        map_pos = engine.find_random_map_pos(game_map, MAP_WIDTH, MAP_HEIGHT, 1, 1, 5, " ")
        pixel_pos = engine.pos_as_pixel(map_pos[0], map_pos[1], TILE_WIDTH, TILE_HEIGHT)
        # TODO hard coded image file muss raus
        monster = Actor("player_dummy")  # erstellt Actor mit fest verdrahtetem player image, da nur so das Image aus den Tiles gesetzt werden kann
        monster._surf = tile_images["Z"]   # Monster-Bild aus Textur-Paket holen ("Z" steht für Zombie ;-)
        monster.left = pixel_pos[0]
        monster.top = pixel_pos[1]
        engine.resize_actor(monster, TILE_WIDTH, TILE_HEIGHT)
        monsters.append(monster)

        allowed_directions = engine.allowed_directions(monster, game_map, MAP_WIDTH, MAP_HEIGHT, TILE_WIDTH, TILE_HEIGHT, "x")
        # print(pixel_pos)
        # print(allowed_directions)
        # Wenn keine Richtungen erlaubt sind (= eingeschlossen): Bleibe am Platz
        if len(allowed_directions) == 0:
            allowed_directions.append(5)  # 5 = don't move
        monster_directions.append(allowed_directions[randint(0, len(allowed_directions) - 1)])


def move_monster(monster_index):

    monster = monsters[monster_index]
    direction = monster_directions[monster_index]

    richtung_aendern = randint(1, 10)

    # Nur die Zahl 1 (von 10 möglichen) ändert die Richtung, außer die Bewegungsrichtung ist geblockt
    if richtung_aendern == 1 \
        or engine.can_move(monster, direction, game_map, MAP_WIDTH, MAP_HEIGHT, TILE_WIDTH, TILE_HEIGHT, "xh") == False:

        allowed_directions = engine.allowed_directions(monster, game_map, MAP_WIDTH, MAP_HEIGHT, TILE_WIDTH, TILE_HEIGHT, "xh")
        if len(allowed_directions) > 0:     # change direction only if possible
            direction = allowed_directions[randint(0, len(allowed_directions) - 1)]
            monster_directions[monster_index] = direction


    engine.move_actor(monster, direction, TILE_WIDTH, TILE_HEIGHT, move_interval)


def check_monster_contact():
    global game_over

    for monster in monsters:
        # print(player.colliderect(monster))
        if player.colliderect(monster):
            game_over = True
            stop_level()
            # print("Monster" + str(monster.pos))
            # print("Player" + str(player.pos))


# wird in regelmäßigen Zeitabständen aufgerufen, damit sich die Monster nicht zu schnell bewegen
def tick():

    for i in range(len(monsters)):
        move_monster(i)

    check_monster_contact()  # TODO Erkennung ist ungenau wg. Animation (z. B. bewegt sich das Monster nach der Kollision noch einen Schritt)


def initialize_level():
    global tile_images
    global game_map
    global MAP_WIDTH
    global MAP_HEIGHT
    global WIDTH
    global HEIGHT
    global player
    global started

    started = False


    level_index = level
    if level_index > len(level_files):
        level_index = len(level_files)

    map_file = level_files[level_index - 1][0]
    tile_img_file = level_files[level_index - 1][1]

    game_map = engine.load_game_map(map_file)

    # Breite und Höhe der Karte ermitteln und merken
    MAP_WIDTH = len(game_map[0])
    MAP_HEIGHT = len(game_map)

    # Fenster-Größe an Map-Größe anpassen
    WIDTH = MAP_WIDTH * TILE_WIDTH
    HEIGHT = MAP_HEIGHT * TILE_HEIGHT

    # Lade Textur-Paket
    # engine.read_tile_images("tile_images.txt", tile_images, TILE_WIDTH, TILE_HEIGHT)
    tile_images = engine.load_tile_images(tile_img_file, TILE_WIDTH, TILE_HEIGHT)

    # TODO hard-coded image file muss raus
    player = Actor("slayer1")         # default player
    player._surf = tile_images["P"]   # Player Image wird auch aus "Textur-Paket" geholt
    engine.resize_actor(player, TILE_WIDTH, TILE_HEIGHT)
    player_pos = engine.pos_as_pixel(1, 1, TILE_WIDTH, TILE_HEIGHT)
    player.left = player_pos[0]
    player.top = player_pos[1]

    generate_monsters(level * 2)
    # generate_monsters(100)  # TEST


# Zeit-Begrenzung und die Bewegungs-Geschwindigkeit können abhängig vom Level gesetzt werden!
def start_level(level_move_interval, level_time_limit):
    global started
    global game_over
    global time_limit
    global start_time
    global level_completed
    global move_interval

    started = True
    show_highscores = False
    game_over = False
    level_completed = False
    move_interval = level_move_interval
    time_limit = level_time_limit
    start_time = time()  # time is running now :-)

    clock.unschedule(tick)
    clock.schedule_interval(tick, level_move_interval)


# Stop the game from updating
def stop_level():
    global started

    clock.unschedule(tick)
    started = False

    # TODO Zeigt "Game Over" erst nach Abfrage des Namens an. Draw() wird ignoriert.
    # TODO Refactoring in eine "isHighscore"-Funktion
    if game_over and highscores.is_highscore (score):  # score > highscores[-1][0] or len(highscores) < MAX_HIGHSCORE_ENTRIES):
        # draw()
        ask_username()
        highscores.add_highscore(score, username)
        highscores.save_highscore()


def update():
    global game_over

    # Zeit abgelaufen?
    # TODO doppelte Berechnungslogik für remaining_time (ähnlich wie in draw()) -> nur einmal implementieren!
    if started and not game_over and not level_completed and (time() - start_time) > time_limit:
        game_over = True
        stop_level()


def draw():
    global remaining_time

    screen.clear()

    # draw game map
    for line_no in range(len(game_map)):
        line = game_map[line_no]
        for col_no in range(len(line)):
            tile = line[col_no]
            # print(tile)
            # Paint the tile if a tile image exists for the tile (code).
            # The space character eg. is not found leaving the black background
            if tile in tile_images:  # tile != " ":
                screen.blit(tile_images[tile], (col_no * TILE_WIDTH, line_no * TILE_HEIGHT))

    if started and not game_over and not level_completed:
        remaining_time = time_limit - round(time() - start_time)

    screen.draw.text("Time: " + str(remaining_time), pos = (20, 10), fontsize = 40, background = "dark gray")
    screen.draw.text("Level: " + str(level), pos = ((WIDTH / 2) - 100, 10), fontsize = 40, background = "dark gray")
    screen.draw.text("Score: " + str(score), pos = (WIDTH - 220, 10), fontsize = 40, background = "dark gray")

    player.draw()

    for monster in monsters:
        monster.draw()

    if not started and not game_over and not level_completed:
        screen.draw.text("F = Switch to Full Screen Size", engine.pos_as_pixel(2, 3, TILE_WIDTH, TILE_HEIGHT), fontsize = 40, color = "red", background = "white")
        screen.draw.text("W = Switch to Window Size", engine.pos_as_pixel(2, 4, TILE_WIDTH, TILE_HEIGHT), fontsize = 40, color = "red", background = "white")
        screen.draw.text("Q = Quit game", engine.pos_as_pixel(2, 5, TILE_WIDTH, TILE_HEIGHT), fontsize = 40, color = "red", background = "white")
        screen.draw.text("Press <space> to start the game!", engine.pos_as_pixel(2, 7, TILE_WIDTH, TILE_HEIGHT), fontsize = 40, color = "red", background = "white")
        pos = engine.pos_as_pixel(round(MAP_WIDTH / 2) + 3, 3, TILE_WIDTH, TILE_HEIGHT)
        highscores.display_highscores(screen, pos[0], pos[1])

    if game_over == True:
        screen.draw.text("GAME over! Your score is: " + str(score), center = (WIDTH / 2, HEIGHT / 2), fontsize = 60, color = "red", background = "white")
        screen.draw.text("Press <space> to continue or Q to Quit", center = (WIDTH / 2, (HEIGHT / 2) + 100), fontsize = 60, color = "red", background = "white")

    if level_completed:
        screen.draw.text("Congrats, level completed in " + str(time_limit - remaining_time) + " seconds! Your score is: " + str(score), center = (WIDTH / 2, HEIGHT / 2), fontsize = 40, color = "red", background = "white")
        screen.draw.text("Press <space> to continue with the next level or Q to Quit", center = (WIDTH / 2, (HEIGHT / 2) + 100), fontsize = 40, color = "red", background = "white")


def on_key_down(key):
    global level_completed
    global game_over
    global remaining_time
    global score
    global level
    global show_highscores

    if key == keys.SPACE:
        if level_completed:
            level = level + 1
        if game_over:
            level = 1
            score = 0
            game_over = False   # nach Game Over zum Hauptmenü zurück mit Space (statt gleich wieder neu zu starten): Damit Highscore angezeigt wird
        elif not started:
            initialize_level()
            start_level(level_move_interval= 0.7, level_time_limit = 30)   # move_speed und level time limit to finish the level

    if started and not game_over and not level_completed:
        direction = 5          # don't move
        if key == keys.LEFT:   # if keyboard.left:
            direction = 1
        if key == keys.RIGHT:
            direction = 2
        if key == keys.UP:
            direction = 3
        if key == keys.DOWN:
            direction = 4

        if engine.can_move(player, direction, game_map, MAP_WIDTH, MAP_HEIGHT, TILE_WIDTH, TILE_HEIGHT, "x"):
            engine.move_actor(player, direction, TILE_WIDTH, TILE_HEIGHT)
            check_monster_contact()

        map_pos = engine.pos_in_map(player.left, player.top, TILE_WIDTH, TILE_HEIGHT)

        tile = engine.tile_at_map_pos(game_map, map_pos[0], map_pos[1])
        if tile == "h":                 # Haus = Level completed
            level_completed = True
            remaining_time = time_limit - round(time() - start_time)  # TODO doppelter Code (siehe draw() -> in Funktion auslagern)
            score = score + (10 * remaining_time)
            stop_level()
        if tile == "a":     # Apfel
            score = score + 50
            engine.set_tile_at_map_pos(game_map, map_pos[0], map_pos[1], " ")   # Apfel entfernen (wurde ja "aufgegessen"

    if key == keys.Q:           # Press the Q key to quit the game (without an "are you sure" question yet ;-)
        raise SystemExit()

    if key == keys.F:
        # screen.surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        # TODO Full Screen wird nach jedem Level, der eine andere Größe hat, wieder in Fenster-Modus geändert
        screen.surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    elif key == keys.W:
        screen.surface = pygame.display.set_mode((WIDTH, HEIGHT))



# ---- Einstiegsstelle bei Programmstart ("main") ------------------

print("pgzero version: " + pgzero.__version__)


# TODO Refactoring abschließen
myGame = g.Game(level_files, TILE_WIDTH, TILE_HEIGHT)
myGame2 = g.Game(level_files, TILE_WIDTH, TILE_HEIGHT)



print("Max_Width:", myGame.get_required_screen_width())
print("Max_Heigth:", myGame.get_required_screen_height())
print("__name__ =", __name__)  # surprisingly "pgzero.builtins"


highscores = hs.Highscores(HIGHSCORE_FILE_NAME, MAX_HIGHSCORE_ENTRIES)
highscores.load_highscores()
# print(highscores)
# highscores.add_highscore(120, "Joe")
# add_highscore(90, "Jane")
# add_highscore(1000, "Hans")
# add_highscore(1200, "Jim")
# add_highscore(1400, "Jack")
# print(highscores)
# add_highscore(600, "Jenny")
# print(highscores)
# highscores.save_highscore()


# The first level is initialized twice (changing the initially shown monster positions!)
# Das ist aber konsistent mit Game Over: Letzter Spielzustand wird angezeigt, bis man im Level 1 neu startet
initialize_level()


pgzrun.go()

# print("Name:", ask_username())

