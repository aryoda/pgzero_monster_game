import json
import os
import pgzero


# from Zombie_Game import highscores_file_name, highscores


class Highscores:

    # _highscores = None  # Highscore-Liste mit Score/Name-Tupeln als Elemente
    # _highscores_file_name = "highscores.json"
    # _max_highscore_entries = 10

    def __init__(self, highscores_file_name = "highscores.json", max_highscore_entries = 10):

        self._highscores_file_name = highscores_file_name
        self._max_highscore_entries = max_highscore_entries
        self._highscores = [(100, "Are you better?")]

    def save_highscore(self):

        with open(self._highscores_file_name, "w") as hs_file:
            json.dump(self._highscores, hs_file)


    def load_highscores(self):

        if os.path.isfile(self._highscores_file_name):
            with open(self._highscores_file_name, "r") as hs_file:
                self._highscores = json.load(hs_file)

        # workaround: Highscore wird immer als List of list gelesen, daher wieder in list of tuples konvertieren
        #             Background: https://realpython.com/python-json/
        for i in range(len(self._highscores)):
            self._highscores[i] = tuple(self._highscores[i])

        # auf die akt. max. Anzahl ein Einträgen reduzieren
        self._highscores = self._highscores[:self._max_highscore_entries]

        return self._highscores


    def is_highscore(self, score):

        if (score > self._highscores[-1][0] or len(self._highscores) < self._max_highscore_entries):
            return True

        return False


    def add_highscore(self, your_score, your_name):

        self._highscores.append((your_score, your_name))

        self._highscores.sort(reverse = True)

        # nur die gewünschte Anzahl an Einträgen behalten
        self._highscores = self._highscores[:self._max_highscore_entries]

        return self._highscores


    # TODO screen-Objekt sollte global sichtbar sein von pgzrun
    # Workaround: Das screen-Objekt von pgzero muss mit übergeben werden,
    # da es von pgzrun erst zur Laufzeit erzeugt wird und aus irgendeinem Grund
    # in diesem Modul nicht sichtbar ist (obwohl screen global ist).
    def display_highscores(self, screen, x, y):

        screen.draw.text("Highscores:", (x, y), fontsize = 40, color = "red", background = "white")

        for i in range(len(self._highscores)):
            y = y + 28
            text = str(i + 1) + ")  " + str(self._highscores[i][0]) + " - " + self._highscores[i][1]
            screen.draw.text(text, (x, y), fontsize = 40, color = "red", background = "white")