#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#  ##############################################################################
#   Auteurs         :   Gerber Cedric
#                       Martins Gomes Rafael
#   Date de debut   :   28 septembre 2015
#   Date de fin     :   10 janvier 2016
#   Etablissement   :   hepia
#   Filiere         :   3eme ITI
#   Cours           :   Reseau I
#
#   Nom fichier     :   Client.py
# ##############################################################################
import socket  # Import socket module

from constants import *
from object_snake import *
from object_foods import *
from scores import *
from preferences import Preferences
from banner import *
from timer import *
from snakePost import snakePost


class Client(snakePost):
    def __init__(self, ip=UDP_ADD_IP, port=UDP_NUM_PORT, couleur="blue", nickname="invite", udp=False):
        super(Client, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), ip, port, couleur, nickname, udp)
        self.addIP = ip
        self.nPort = int(port)

        pygame.init()
        self.clientConnexion()
        print "Connected"

        self.listBody = []
        self.snakes = {}
        self.listFood = []
        self.host = None
        self.nickname = nickname
        self.ready = False

        # get preferences
        self.preferences = Preferences()

        # resolution, flags, depth, display
        self.unit = Constants.RESOLUTION[0]/Constants.UNITS
        self.banner = Banner()
        self.score_width = self.unit*15

        if self.preferences.fullscreen:
            self.screen = pygame.display.set_mode((Constants.RESOLUTION[0]+self.score_width,
                                                   Constants.RESOLUTION[1]), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((Constants.RESOLUTION[0]+self.score_width,
                                                   Constants.RESOLUTION[1]), 0, 32)

        pygame.display.set_caption(Constants.CAPTION)

        # game area surface
        self.gamescreen = pygame.Surface(Constants.RESOLUTION)
        # score area rectangle surface
        self.scorescreen = pygame.Surface((self.score_width, Constants.RESOLUTION[1]))

        # Snake and foods manager
        self.me = Snake(color=pygame.color.THECOLORS[self.couleur], nickname=self.nickname)

        # self.nickname = self.preferences.get("nickname")
        self.f = Foods()

        # Score manager
        self.scores = Scores((self.score_width, Constants.RESOLUTION[1]))

        # add our own score, the server will send us the remaining one at connection
        self.scores.new_score(self.nickname, pygame.color.THECOLORS[self.couleur])

        # game area background color
        self.gamescreen.fill(Constants.COLOR_BG)
        self.scorescreen.fill((100, 100, 100))

        # timers
        self.clock = pygame.time.Clock()
        self.current_time = 0

        self.move_snake_timer = Timer(1.0/Constants.SNAKE_SPEED*1000, self.current_time, periodic=True)
        self.blink_snake_timer = Timer(1.0/Constants.SNAKE_BLINKING_SPEED*1000, self.current_time, periodic=True)
        self.blink_banner_timer = Timer(500, self.current_time, periodic=True)
        self.new_apple_timer = Timer(Constants.NEW_APPLE_PERIOD*1000, self.current_time, periodic=True)

    def process_events(self):
        # cle handling
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_UP:
                    self.me.action(1)
                if event.key == pygame.K_DOWN:
                    self.me.action(2)
                if event.key == pygame.K_LEFT:
                    self.me.action(3)
                if event.key == pygame.K_RIGHT:
                    self.me.action(4)
                if event.key == pygame.K_SPACE:
                    if not self.ready:
                        self.msgReady()
                        self.me.set_ready()
                    else:
                        print "Le joueur : " + self.nickname + " est deja 'ready'."

    def run(self):
        self.running = True
        while self.running:
            # time tracking
            self.current_time += self.clock.tick(Constants.FPS)

            # check if we need to move our own snake's state if we do, send an update of our position to the server
            if self.move_snake_timer.expired(self.current_time):
                self.me.move()
                self.msgBody_p()

            if self.blink_snake_timer.expired(self.current_time):
                for s in self.snakes:
                    self.snakes[s].blink()

            # cleanup background
            self.gamescreen.fill(Constants.COLOR_BG)

            # draw scores
            self.scores.draw(self.screen)

            # draw all snakes positions as last seen by the server
            # we do not compute their positions ourselves!
            # self.me.draw(self.gamescreen)
            for cle in self.snakes:
                self.snakes[cle].draw(self.gamescreen)

            # draw food
            self.f.draw(self.gamescreen)

            # process external events (cleboard,...)
            self.process_events()

            # then update display, update game area on screen container
            self.screen.blit(self.gamescreen, (self.score_width, 0))

            pygame.display.update()
            self.gestionEvennement()

            data, self.host = self.ecouteClient()
            if data is not None:
                donneeJson = json.loads(data)
                for cle in donneeJson:
                    if cle == "foods":
                        self.f.set_positions(donneeJson[cle])
                    elif cle == "snakes":
                            for players_info in self.snakes.keys():
                                present = False
                                for donnes in donneeJson[cle]:
                                    if donnes[0] == players_info:
                                        present = True
                                if not present:
                                    del self.snakes[players_info]
                                    self.scores.del_score(players_info)
                            for players_info in donneeJson[cle]:
                                if self.snakes.get(players_info[0]):
                                    self.snakes[players_info[0]].setBody(players_info[1])
                    elif cle == "players_info":
                        for players_info in donneeJson[cle]:
                            if not self.snakes.get(players_info[0]):

                                self.snakes[players_info[0]]= Snake(color=pygame.color.THECOLORS[players_info[1]],
                                                                    nickname=players_info[0])
                                self.scores.new_score(players_info[0],self.snakes[players_info[0]].color,players_info[2])
                            else:
                                if players_info[3]:
                                    self.snakes[players_info[0]].set_ready()
                                else:
                                    self.snakes[players_info[0]].set_unready()
                            self.scores.set_score(players_info[0], players_info[2])
                    elif cle == 'game_over':
                        if donneeJson[cle] == self.nickname:
                            self.snakes[donneeJson[cle]].restart()
                            self.me.restart()
                            self.ready = False
                            self.snakes[donneeJson[cle]].set_unready()
                    elif cle == 'grow':
                        self.me.grow(Constants.GROW)
                        self.scores.inc_score(donneeJson[cle], 1)
                    break




    def msgBody_p(self):
        """

        Methode qui envoie la liste qui contient les coordonnées du corp d'un serpent envoie non securisé.
        listBody => contient les positions des différentes parties du corps
        :return:
        """
        # formatage des données en JSON
        send = None
        if self.me.body[0] == None:
            print "liste des corps vides"
        else:
            send = json.dumps({'body_p' : self.me.body})
        self.envoiSnakePost(send, self.host, False)

    # methode qui envoie un message qui dit au serveur si on est ready ou pas
    def msgReady(self):
        # formatage des données en JSON
        msg = {'ready':True}
        self.ready = True
        # envoi fiable --> fiable = True
        self.envoiSnakePost(json.dumps(msg), self.host, True)

if __name__ == "__main__":
    Client(UDP_ADD_IP, UDP_NUM_PORT, "red", "Rafael").run()
