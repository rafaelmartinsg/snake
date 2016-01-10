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
#   Nom fichier     :   Serveur.py
# ##############################################################################
import json

from constants import *
from snakeChannel import *
from snakePost import *
from joueurs import *


class Serveur(snakePost):
    def __init__(self):
        super(Serveur, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), UDP_ADD_IP, UDP_NUM_PORT)
        pygame.init()
        self.horloge = pygame.time.Clock()
        #self.current_time = 0
        self.tempsActuel = 0
        self.addIp = UDP_ADD_IP
        self.nPort = UDP_NUM_PORT
        self.canal.setblocking(False)     # Non-blocking
        self.canal.bind((self.addIp, self.nPort))

        self.clients = {}
        self.listfood = []

        self.listPlayersInfo = []
        self.snakesDico = {}
        print 'Serveur ecoute sur le port : ', self.nPort, '...'

    def run(self):
        while True:
            # controle si des messages sont a envoyer
            self.gestionEvennement()
            # Ecoute d'eventuels messages
            donnees, canal = self.ecouteServeur()

            if donnees is not None:
                if not self.clients.get(canal):
                    self.clients[canal] = Joueurs(self.connexions[canal][C_NICKNAME], self.connexions[canal][C_COULEUR],
                                                  0, False, [])

    def msgFood(self):
        """

        Methode pour les messages food, listFood => liste avec toute les coordonnées des pommes
        :return:
        """
        # formatage des données en JSON
        if self.listFood[0] == None:
            print "liste des pommes vides"
        else:
            self.broadcast(json.dumps({'food': self.listFood}), True)

    def broadcast(self, donnees, fiable=False):
        """

        Methode permettant d'envoyer a tous les joueurs presents dans la liste le meme message
        :param donnees: contient les donnes a envoyer
        :param fiable: determine si l'envoi doit etre fiable ou non
        :return:
        """
        for joueur in self.clients:
            self.envoiSnakePost(donnees, joueur, fiable)

    #
    def msgSnakes(self):
        """

        envoie la liste des positions du corps de tout les snakes dans la partie, préfixées par l'identifiant du joueur.
        snakesDico => dicitonnaire nom du joueur, position
        :return:
        """
        # formatage des données en JSON
        if self.listFood.get(0) is None:
            send = None
            print "dico position du corps vide"
        else:
            long = len(self.snakesDico)
            cpt = 0
            send = '{"snakes": ['
            for i in self.snakesDico:
                cpt += 1
                if cpt < long:
                    send += '["'+i+'",'+json.dumps(self.snakesDico[i])+'],'
                else:
                    send += '["'+i+'",'+json.dumps(self.snakesDico[i])+']'
            send += ']}'

        # envoie non fiable
        self.broadcast(send)

    def msgPlayers_info(self):
        """

        msg contenant toute les infos des joueurs: nom du joueur, sa couleur, son score, ready ou pas
        listPlayersInfo => liste contenant toute les infos
        :return:
        """
        # formatage JSON
        if self.listPlayersInfo[0] is None:
            print "liste des info player vide"
        else:
            for joueur in self.listPlayersInfo:
                self.envoiSnakePost(json.dumps({'players_info': self.listPlayersInfo}), joueur, True)
        pass

    def msgGame_over(self, nomJoueur):
        """

        Contient le nom du joueur qui a perdu et qui doit recommencer depuis le debut
        :param nomJoueur: contient le nickname du joueur
        :return:
        """
        # formatage JSON
        send = json.dumps({'game_over':nomJoueur})
        # envoie fiable
        self.broadcast(send, True)

    def msgGrow(self, nomJoueur):
        """

        Previens un joueur qu'il est rentrer dans une pomme
        :param nomJoueur: contient ne nickname du joueur
        :return:
        """
        # formatage JSON
        send = json.dumps({'grow':nomJoueur})
        # envoie fiable
        self.broadcast(send, True)

if __name__ == "__main__":
    Serveur().run()
