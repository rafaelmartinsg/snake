#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#  ##############################################################################
#   Auteurs         :   Gerber Cedric
#                       Martins Gomes Rafael
#   Date de debut   :   28 septembre 2015
#   Date de fin     :   04 janvier 2016
#   Etablissement   :   hepia
#   Filiere         :   3eme ITI
#   Cours           :   Reseau I
#
#   Nom fichier     :   Serveur.py
# ##############################################################################
import sys

import pygame
import random
import json

from constants import *
from snakeChannel import *
from snakePost import *
from joueurs import *

# Declaration de variables globales

class Serveur(snakePost):
    def __init__(self):
        super(Serveur, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), UDP_ADD_IP, UDP_NUM_PORT)
        pygame.init()
        self.clock = pygame.time.Clock()
        self.current_time = 0
        #self.send_timer = Timer(SEND_INTERVAL, 0, True)
        self.addIp = UDP_ADD_IP
        self.nPort = UDP_NUM_PORT
        self.canal.setblocking(False)     # Non-blocking
        self.canal.bind((self.addIp, self.nPort))

        self.clients = {}
        self.nourriture = []

        #self.listPlayersInfo = []
        #self.snakesDico = {}
        #self.sServeur = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #self.sServeur.bind((self.addIp, self.nPort))
        #super(Serveur, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        print 'Serveur ecoute sur le port : ', self.nPort, '...'


    #
    #   gestionMessage est la methode qui s'occupe des messages recus et ceux que le serveur doit envoyer
    #   Les messages sont definit par le cahier des charges selon la manière suivante :
    #       RX  :   0xffffffff (numero de sequence pour initier la connexion)
    #       RX  :   GetToken A Snake
    #       TX  :   Token B A ProtocoleNumber
    #       RX  :   Connect /nom_cles/valeur_cles/.../...
    #       TX  :   Connected B
    #
    # def gestionMessages(self):
    #     while(True):
    #         self.serveurConnexion()

    def run(self):
        while (True):
            # check si des messages sont a envoyer
            #self.gestionMessages()
            self.process_buffer()
            # Ecoute d'eventuels messages
            donnees, canal = self.ecouteServeur()

            if donnees is not None:
                if not self.clients.get(canal):
                    self.clients[canal] = Joueurs(self.connexions[canal][C_NICKNAME], self.connexions[canal][C_COULEUR],
                                                  0, False, [])
            # else:
                # return None, None

    # Methode pour les messages food, listFood => liste avec toute les coordonnées des pommes
    def msgFood(self):
        # formatage des données en JSON
        if(self.listFood[0] == None):
            print "liste des pommes vides"
        else:
            send = '{"foods": '
            send += json.dumps(self.listFood) + '}'
        #Envoie securisé a tout les clients la liste des pommes
        self.broadcast(send,True)

    def broadcast(self,data,secure):
        if secure:
            for i in self.clients:
                snakePost.envoiSecure(self,self.sServeur,data,i)
        elif not secure:
            for i in self.clients:
                snakePost.envoiNonSecure(self,self.sServeur,data,i)

    #  envoie la liste des positions du corps de tout les snakes dans la partie, préfixées par l'identifiant
    #du joueur. snakesDico => dicitonnaire nom du joueur, position
    def msgSnakes(self):
        # formatage des données en JSON
        if(self.listFood.get(0) == None):
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
        self.broadcast(send,False)

    # msg contenant toute les infos des joueurs: nom du joueur, sa couleur, son score, ready ou pas
    # listPlayersInfo => liste contenant toute les infos
    def msgPlayers_info(self):
        # formatage JSON
        if(self.listPlayersInfo[0] == None):
            print "liste des info player vide"
        else:
            send = '{"players_info": "'
            send += json.dumps(self.listPlayersInfo) + '"}'
        # envoie fiable
        pass

    # Contient le nom du joueur qui a perdu et qui doit recommencer depuis le debut
    def msgGame_over(self,nomJoueur):
        # formatage JSON
        send = '{"game_over":"'+ nomJoueur+'"}'
        # envoie fiable
        self.broadcast(send,True)

    # previens un joueur qu'il est rentrer dans une pomme
    def msgGrow(self,nomJoueur):
        # formatage JSON
        send = '{"grow":"'+ nomJoueur+'"}'
        # envoie fiable
        self.broadcast(send,True)


if __name__=="__main__":
    Serveur().run()
    #serv = Serveur()
    #serv.gestionMessages()
